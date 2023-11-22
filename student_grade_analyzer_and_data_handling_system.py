# importing dependacies
import pandas as pd
from pathlib import Path
from sys import exit as sys_exit
import matplotlib.pyplot as plt

# Defining Constants
SCORE: dict[range, str] = {
    range(90, 101): "A",
    range(80, 90): "B",
    range(60, 80): "C",
    range(50, 60): "D",
    range(34, 50): "E",
    range(1, 34): "F",
}

OPTIONS: list[str] = [
    "show",
    "options",
    "delete",
    "add",
    "exit",
    "avg",
    "grade",
    "compare",
    'empty'
]
running: bool = True
subject_name_marks_mapp: dict[str, float] = {}


# Creates a new CSV data file if one does not already exist in the specified path
def make_csv(file_name: Path = Path("sample.csv")) -> None:
    "Deprecated for now"
    if not file_name.is_file():
        print("File not Found!")
        file_name.touch()
        print("File Created!")


# SHOW ALL THE AVAILABLE FUNTIONS
def show_options() -> str:
    """shows all available functions the user can use in a  formated way"""
    result: str = ""  # store output
    for i, k in enumerate(OPTIONS, 1):
        result += (
            "\n" + f"{i}:  {k.title()}"
        )  # formating the output with proper index and value
    return result


# ==============================================================================================
def update_df(df_of_csv_data: Path) -> pd.DataFrame:
    """gets the most recent data from the file for accurate data analysis by reading the csv file \n
    also helps in handling EmptyDataError"""
    try:  # handling empty csv files
        df_of_csv_data = pd.read_csv(CSV_DATA_PATH)  # reading the data
    except pd.errors.EmptyDataError:
        df_of_csv_data = pd.DataFrame()
    return df_of_csv_data


# ------------------------------------------------------------------------------------------------------n


def delete_entry(df_to_del_entry: pd.DataFrame, name_entry_to_del: str) -> pd.DataFrame:
    "deletes a row from the dataframe upon the user given name"
    return df_to_del_entry.drop(
        df_to_del_entry.loc[df_to_del_entry.Name == name_entry_to_del].index,
        axis="index",
    )


# -------------------------------------------------------------------------------------------------------
def assign_grade(df_with_avg: pd.DataFrame) -> pd.DataFrame:
    '''returns thr dataframe with the grade column which gives grades to students in a range \n
    range(90, 101): "A",\n
    range(80, 90): "B",\n
    range(60, 80): "C",\n
    range(50, 60):  "D",\n
    range(34, 50): "E",\n
    range(1, 34):  "F"'''

    if "Average" not in df_with_avg.columns:
        print("ERROR!")
        print("No average column found!")
        return df_with_avg
    grades_arr: list[str] = []
    avg_arr: list[int] = [round(i) for i in df_with_avg["Average"]]
    for avg_val in avg_arr:
        for score_key in SCORE:
            if avg_val in score_key:
                grades_arr.append(SCORE[score_key])
    df_with_avg["Grade"] = grades_arr
    return df_with_avg


# ------------------------------------------------------------------------------------------------------------
def add_entry(
    std_name: str, no_subs: int, prev_df_empty: bool, csv_file_name: Path
) -> None:
    """Adds a student name and thier marks in the dataframe provided by the user\n
    if the CSV file provided is empty , user will be asked to input column names"""
    # looping total number of   #subject times to recieve input
    if no_subs < 1:
        print("ERROR!")
        print(
            "Number of subjects should be greater than 0"
        )  # check for number of inputs
        sys_exit(1)
    if (
        prev_df_empty
    ):  # if csv file is empty ask the user for subject names to set as columns
        for _ in range(no_subs):
            subject_name = input("Enter the name of the subject:\n")
            subject_marks = float(
                input(f"Enter the marks of student in {subject_name}:\n")
            )
            subject_name_marks_mapp[subject_name] = subject_marks
    else:  # else set the marks directly as columns already exist
        for i in update_df(csv_file_name).columns[1:]:
            if i not in (
                "Average",
                "Grade",
            ):  # avoid the program asking user to input data in the avg column pr grade column
                subject_marks = float(input(f"Enter the marks of student in {i}:\n"))
                subject_name_marks_mapp[i] = subject_marks

    print("Data Recieved")
    # Creating/Updating DataFrame
    student_subject_marks_df = pd.DataFrame(
        [[std_name, *list(subject_name_marks_mapp.values())]],
        columns=["Name", *list(subject_name_marks_mapp.keys())],
    )
    # seting mode for csv to append to add new data and checking if csv is empty to check if to include header
    student_subject_marks_df.to_csv(
        path_or_buf=csv_file_name, mode="a", index=False, header=prev_df_empty
    )
    print(f"data stored to {csv_file_name}")


# -------------------------------------------------------------------------------------------------------

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


def calc_avg(df_csv_val: pd.DataFrame, mode: str = "all") -> pd.DataFrame | float:
    """Calculates the average of all or of a specefic student \n
    args:\n
    df_csv_val: The Dataframe on which the average calculation is supposed to take place\n
    mode: if mode is set to 'all' , calculates the average of all students and returns a Dataframe else
     if mode is set to 'single' returns the average of a single student whose name is provided
    """
    if mode == "all":
        vals: list[float] = []  # store the average of students to add to column later
        for i in range(df_csv_val.shape[0]):
            if i != -1:
                vals.append(df_csv_val.iloc[i, 1:-1].mean())
        df_cs_val_copy_for_print = df_csv_val.copy()
        df_cs_val_copy_for_print["Average"] = vals  # adding average column
        df_csv_val["Average"] = vals
        return df_csv_val

    elif mode == "single":
        student_name_avg = input(
            "Enter the name of the student whose average is needed:\n"
        )
        # using generator to return a single value of student whose average is needed
        return next(
            pd.Series(i).iloc[1:].mean()
            for i in df_csv_val.values
            if student_name_avg in i
        )


# --------------------------------------------------------------------------------------------------------


def compare_vals(
    df_of_data_for_comparision: pd.DataFrame | pd.Series,
    mode: str,
) -> None:
    """compares marks of students in a graphical way\n
    mode can be selected to compare all or selected students only\n
    comparion is done based on the average column"""
    if "Average" not in df_of_data_for_comparision.columns:
        df_of_data_for_comparision:pd.DataFrame = calc_avg(df_of_data_for_comparision)
    if mode == "all":
        df_of_data_for_comparision.plot(
            kind="bar", xlabel="Names", ylabel="Marks"
        )
        plt.xticks(
            list(range(0, len(df_of_data_for_comparision["Name"]))),
            df_of_data_for_comparision.Name,
        )
        plt.show()
    elif mode == "some":
        stds_for_comp: list[str] = input(
            "Enter the name of students whose marks are to be compared(comma seperated):\n"
        ).split(",")
        data_to_compare: list[int] = [
            list(i)[-2]
            for i in df_of_data_for_comparision.values
            if i[0] in stds_for_comp
        ]
        plt.bar(stds_for_comp, data_to_compare, width=0.20)
        plt.xlabel("Names")
        plt.ylabel("Marks")
        plt.show()

#------------------------------------------------------------------------------------------------------
def user_input_handling(user_input:str,type_match:type=int):
    '''matches a user input to a given type(int by default)'''
    user_input:str = user_input.lower()
    while True:
        if user_input == 'exit':
            print('Exiting Program')
            sys_exit(1)
        try:
            user_input = type_match(user_input)
            return user_input
        except ValueError:
            print('Invalid Input!')
            user_input = input('Enter the input again:\n')
# ------------------------------------------------------------------------------------------------------
# Main program start
print(
    """----------------------------------------------------------------------------
        ....Welcome to Student Grade Handler and Data Handler system....\n Please provide path to a csv file 
      -----------------------------------------------------------------------------"""
)

CSV_DATA_PATH = Path(input("Enter:\n"))


if not CSV_DATA_PATH or not CSV_DATA_PATH.is_file():  # handle invalid inputs
    print("ERROR!")
    print("Invalid file path")
    exit(1)
print("\n")
print("File Path recieved")

df_of_csv_data = update_df(CSV_DATA_PATH)  # get the data from the dataframe
if df_of_csv_data.empty:
    print('Empty CSV file detected')
    no_subjects = user_input_handling(input("Enter the number of subjects to be stored:\n"),int)
else:
    no_subjects = df_of_csv_data.shape[1] - 1  # avoid adding Name column to subjects

print(f"Commands:{show_options()}")  # showing all the features to the user
while running:
    command = input("Enter any command:\n").lower()
    if command not in OPTIONS:  # checking if user provided a valid command
        print("ERROR!")
        print("COMMAND NOT RECONGNIZED")
    if command == "add":
        df_of_csv_data = update_df(CSV_DATA_PATH)
        student_name = input(
            "Enter the name of the student:\n"
        ).title()  # capitalize the Name

        add_entry(student_name, no_subjects, df_of_csv_data.empty, CSV_DATA_PATH)
    if command == "exit":
        print("EXITING...")
        exit(0)  # 0 for success
    if command == "show":
        print(update_df(CSV_DATA_PATH))
    if command == "avg":
        df_of_csv_data = update_df(CSV_DATA_PATH)
        if (
            input(
                "Calculate average of all students and return another column(C) added to data or find a average for a particular student(S):\n"
            ).lower()
            == "s"
        ):
            choice_of_user_for_avg = "single"
        else:  # for all other inputs do all for minimal crashes
            choice_of_user_for_avg = "all"
        df_csv_data_with_avg = calc_avg(df_of_csv_data, choice_of_user_for_avg)
        print(df_csv_data_with_avg)
        print(
            "-------------------------------------------------------------------------"
        )
        if choice_of_user_for_avg == "all":
            print(r"Save Average column to csv file?(Y\N):")
            if input("Enter:\n").lower() == "y":
                print("Data saved...")
                df_csv_data_with_avg.to_csv(CSV_DATA_PATH, index=False)
    if command == "options":
        print(show_options())

    if command == "delete":
        df_of_csv_data = update_df(CSV_DATA_PATH)
        name_entry_to_delete = input(
            "Enter the name of the student whose entry is to be deleted:\n"
        )
        df_of_csv_data = delete_entry(df_of_csv_data, name_entry_to_delete)
        print(df_of_csv_data)
        save_del_csv_data = input(f"Save the data to {CSV_DATA_PATH}?(Y/N):\n").lower()
        if save_del_csv_data == "y":
            df_of_csv_data.to_csv(CSV_DATA_PATH, header=True, index=False, mode="w")
            print("Data Saved..")
        else:
            print("Data not Saved..")

    if command == "grade":
        df_of_csv_data = update_df(CSV_DATA_PATH)
        df_of_csv_data = assign_grade(df_of_csv_data)
        print(df_of_csv_data)
        if "Grade" not in df_of_csv_data.columns:
            print("Returning original data")
            continue
        save_grade_df = input(f"Save the data to {CSV_DATA_PATH}?(Y/N):\n").lower()
        if save_grade_df == "y":
            df_of_csv_data.to_csv(
                CSV_DATA_PATH,
                index=False,
            )
            print("Data saved")
        else:
            print("Data was not saved")
    if command == "compare":
        compare_all_or_some = input(
            "Compare all students in the dataframe(Y) or a selected few(N):\n"
        ).lower()
        df_of_csv_data = update_df(CSV_DATA_PATH)
        if compare_all_or_some == "y":
            compare = "all"
        else:
            compare = "some"
        compare_vals(df_of_csv_data, compare)
    if command =='empty':
        print('''Are you sure you want to empty the csv file?\n
              ONCE THE FILE IS EMPTIED IT CANNOT  BE RECOVERED
              ''')
        if input('''Enter 'Y' to continue or any other cancel:\n''').lower() == 'y':
            with open(CSV_DATA_PATH,mode='w') as csv_file_to_empty:
                csv_file_to_empty.write('')
        else:
            print('DELETION CANCELLED')
    
