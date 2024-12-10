import pandas as pd

class User:
    def __init__(self, income, interest):
        self.income = income
        self.interest = interest
        #self.period = period
        self.df = self._read_table()


    def _read_table(self):
        file_name = 'table.txt' 
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
    

    def find_max_expense(self):
        bracket = self._find_interest_bracket(self.interest, self.df.columns)
        if bracket is None:
            return "Invalid interest rate."
        if self.income in self.df.index:
            return self.df.loc[self.income, bracket]
        else:
            return "Invalid income."
    
def main():
    income = 28000
    interest = 1.6
    user = User(income, interest)
    print(user.find_max_expense())

if __name__ == "__main__":
    main()
