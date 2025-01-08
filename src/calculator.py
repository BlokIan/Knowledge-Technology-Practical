import pandas as pd


class User:
    def __init__(self, income, interest, period):
        self._income = income
        self._interest = interest
        self._period = period
        self._expense_table = self._read_expense_table()
        self._annuity_table = self._read_annuity_table()

    def _read_expense_table(self):
        file_name = 'woonquote.txt' 
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
        bracket = self._find_interest_bracket(self._interest, self._expense_table.columns)
        if bracket is None:
            return "Invalid interest rate."
        if self._income in self._expense_table.index:
            return self._expense_table.loc[self._income, bracket]
        else:
            return "Invalid income."
        
    def _read_annuity_table(self):
        file_name = 'annuity.txt' 
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
        if self._interest in self._annuity_table.index:
            return self._annuity_table.loc[self._interest, self._period]
        else:
            return "Invalid interest rate."
        
    def find_max_mortgage(self):
        return (self._find_max_expense() / 100) * (self._income / 12) * self._find_annuity_factor()
    
def main1():
    income = 28000
    interest = 1.6
    period = 360
    user = User(income, interest, period)
    print(user._find_max_expense())
    print(user._find_annuity_factor())
    print(user.find_max_mortgage())

def main():
    income = 28000
    interest = 3.3
    period = 360
    user = User(income, interest, period)
    print(user._find_max_expense())
    print(user._find_annuity_factor())
    print(user.find_max_mortgage())

if __name__ == "__main__":
    main()
