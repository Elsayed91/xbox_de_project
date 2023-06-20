import sys


def read_xcom(xcom_value):
    print(xcom_value)


if __name__ == "__main__":
    # Read the xcom_value argument
    xcom_value = sys.argv[1]

    # Call the read_xcom function with the provided value
    read_xcom(xcom_value)
