import sys
import streamlit as st
from streamlit.web import cli as stcli


def main():
    """
    Start the Streamlit chat application using the specified FAISS index.
    """
    sys.argv = [
        "streamlit",
        "run",
        "chat.py",
        "--",
        "--folder=recipes",
    ]

    sys.exit(stcli.main())


if __name__ == "__main__":
    try:
        main()

    except Exception as e:
        st.write("Fatal Error!")
        st.write(e)
