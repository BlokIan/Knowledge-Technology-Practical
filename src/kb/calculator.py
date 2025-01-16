import pandas as pd
import os
import math
WOONQUOTE_FILEPATH = os.path.join(os.getcwd(), "src", "kb", "woonquote.txt")
ANNUITY_FILEPATH = os.path.join(os.getcwd(), "src", "kb", "annuity.txt")

class User:
    def __init__(self, income, interest, period, energy_label, market_value, monthly_costs, student_debt):
        self._income = round(income, -3)
        self._interest = interest
        self._period = period
        self._energy_label = energy_label
        self._market_value = market_value
        self._month_interest = interest / 100 / 12
        self._costs = monthly_costs
        self._student_debt = student_debt
        self._perc_interest_deduction = 0.3697 # 2025 value: 0.3748
        self._expense_table = self._read_expense_table()
        self._annuity_table = self._read_annuity_table()
        self._bracket= None
        self._max_mortgage = None

    def _read_expense_table(self):
        file_name = WOONQUOTE_FILEPATH
        df = pd.read_csv(file_name, delimiter="\t", encoding="utf-8")

        df.columns = df.columns.str.strip()
        df["Income"] = (
            df["Income"]
            .str.replace("€", "") 
            .str.replace(".", "")  
            .str.strip()
            .astype(int)
        )

        percentage_columns = df.columns[1:]  
        for col in percentage_columns:
            df[col] = (
                df[col]
                .str.replace("%", "")  
                .str.replace(",", ".")  
                .astype(float)
            )

        df.set_index("Income", inplace=True)

        return df

    def _find_interest_bracket(self, rate, brackets):
        for bracket in brackets:
            bounds = bracket.replace("%", "").split("-")
            lower_bound = float(bounds[0].replace(",", "."))
            upper_bound = float(bounds[1].replace(",", ".")) 

            if lower_bound <= rate <= upper_bound:
                return bracket
        return None
    
    def _find_max_expense(self):
        self._bracket = self._find_interest_bracket(self._interest, self._expense_table.columns)
        if self._bracket is None:
            return "Invalid interest rate."
        income = self._income
        if self._income < 28000:
            income = 28000
        if income in self._expense_table.index:
            return self._expense_table.loc[income, self._bracket]
        else:
            return "Invalid income."
        
    def _read_annuity_table(self):
        file_name = ANNUITY_FILEPATH
        df = pd.read_csv(file_name, delimiter="\t", encoding="utf-8")

        df.columns = df.columns.str.strip()  
        del df["Per maand"] 

        df["Interest"] = (
            df["Interest"]
            .str.replace("%", "") 
            .str.strip()
            .astype(float)
        )

        factor_columns = df.columns[1:]  
        df.rename(columns={col: int(col) for col in factor_columns}, inplace=True)

        df.set_index("Interest", inplace=True) 

        return df 
    
    def _find_annuity_factor(self):
        if math.ceil(self._interest*10)/10 in self._annuity_table.index:
            return self._annuity_table.loc[math.ceil(self._interest*10)/10, self._period]
        else:
            return "Invalid interest rate."
    
    def _extra_mortgage_energy_label(self):
        """Returns the extra mortgage a user can receive given the energy label."""
        match self._energy_label:
            case "A++++ with energy performance guarantee":
                return 50000
            case "A++++":
                return 40000
            case "A+++":
                return 30000
            case "A++, A+":
                return 20000
            case "A, B":
                return 10000
            case "C, D":
                return 5000
            case "E, F, G":
                return 0 
            
    def _less_mortgage_student_debt(self):
        if self._student_debt is None or type(self._student_debt) == str:
            return 0
        factor = 0
        match self._bracket:
            case "0,000-1,500%" | "1,500-2,000%":
                factor = 1.05
            case "2,001-2,500%":
                factor = 1.1
            case "2,501-3,000%":
                factor = 1.15
            case "3,001-3,500%" | "3,501-4,000%":
                factor = 1.2
            case "4,001-4,500%":
                factor = 1.25
            case "4,501-5,000%" | "5,001-5,500%":
                factor = 1.3
            case "5,501-6,000%":
                factor = 1.35
            case "6,001-6,500%" | "6,501-100,000%":
                factor = 1.4
        return (factor * self._student_debt / (self._month_interest / (1 - (1 + self._month_interest) ** -(self._period))))
    
    def _year_deductible_interest(self, annuity_gross_monthly_costs):
        annuity_mortgage = self._max_mortgage
        linear_mortgage = self._max_mortgage
        annuity_year_deductible_interest = 0
        linear_year_deductible_interest = 0

        for _ in range(12):
            linear_year_deductible_interest += linear_mortgage * self._month_interest
            linear_mortgage -= linear_mortgage/self._period
            
            amount_interest = annuity_mortgage * self._month_interest
            annuity_mortgage -= annuity_gross_monthly_costs - amount_interest
            annuity_year_deductible_interest += amount_interest

        return annuity_year_deductible_interest, linear_year_deductible_interest
        
    def _notional_rental_value(self):
        if self._woz <= 12500:
            return 0
        elif self._woz <= 25000:
            return 0.0010 * self._woz
        elif self._woz <= 50000:
            return 0.0020 * self._woz
        elif self._woz <= 75000:
            return 0.0025 * self._woz
        elif self._woz <= 1310000:
            return 0.0035 * self._woz  
    
    def _annuity_costs(self):
        return self._max_mortgage * (self._month_interest / (1 - (1 + self._month_interest) ** -self._period))
    
    def _linear_costs(self):
        linear_mortgage_repayment = self._max_mortgage / self._period
        linear_interest_payment = 0
        linear_mortgage = self._max_mortgage

        for _ in range(12):
            linear_interest_payment += self._month_interest * linear_mortgage
            linear_mortgage -= linear_mortgage_repayment

        return linear_mortgage_repayment + linear_interest_payment / 12

    def _new_max_mortgage(self):
        return (self._annuity_costs() - self._costs) / (self._month_interest / (1 - (1 + self._month_interest) ** -self._period))
    
    def find_max_mortgage(self):
        self._max_mortgage = int(round((self._find_max_expense() / 100) * (self._income / 12) * self._find_annuity_factor(),0))
        self._max_mortgage += self._extra_mortgage_energy_label() - self._less_mortgage_student_debt()
        self._max_mortgage = self._new_max_mortgage()
        if self._max_mortgage > self._market_value:
            self._max_mortgage = self._market_value
        
        return round(self._max_mortgage)
    
    def monthly_costs(self):
        if self._max_mortgage is None:
            self.find_max_mortgage()

        annuity_gross_monthly_costs = self._annuity_costs()
        linear_gross_monthly_costs = self._linear_costs()

        annuity_year_deductible_interest, linear_year_deductible_interest = self._year_deductible_interest(annuity_gross_monthly_costs)
        notional_rental_value = self._notional_rental_value()

        annuity_mortgage_interest_deduction = (annuity_year_deductible_interest - notional_rental_value) * self._perc_interest_deduction
        linear_mortgage_interest_deduction = (linear_year_deductible_interest - notional_rental_value) * self._perc_interest_deduction
        annuity_net_monthly_costs = annuity_gross_monthly_costs - annuity_mortgage_interest_deduction / 12
        linear_net_monthly_costs = linear_gross_monthly_costs - linear_mortgage_interest_deduction / 12

        return math.ceil(annuity_gross_monthly_costs), math.ceil(annuity_net_monthly_costs), math.ceil(linear_gross_monthly_costs), math.ceil(linear_net_monthly_costs)
    
def main1():
    income = 100000
    interest = 1.6
    period = 360
    woz = 200000
    user = User(income, interest, period, woz)
    print(user._find_max_expense())
    print(user._find_annuity_factor())
    print(user.find_max_mortgage())

def main():
    income = 50000
    interest = 3.78
    period = 360
    energy_label = "A+++"
    woz = 133727
    monthly_costs = 0
    user = User(income, interest, period, energy_label, woz, monthly_costs)
    print(user._find_max_expense(), user._find_annuity_factor())
    print(user.find_max_mortgage())
    
    print(user.monthly_costs())

if __name__ == "__main__":
    main()
