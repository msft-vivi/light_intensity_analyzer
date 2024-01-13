# Content

## Environment Setup

- Clone the repository

    ```git
    git clone git@github.com:msft-vivi/light_intensity_analyzer.git
    ```

- Navigate to the project directory in the terminal (Powershell or Command Prompt)

    ```
    cd Spectrum
    ```

- Create a new virtual environment

    ```python
    python -m venv <name>

    e.g:
    python -m venv tkinter

    now the new virtual environment `tkinter` is created in the current directory
    ```

- Activate the virtual environment

    ```python
    .\tkinter\Scripts\activate
    ```

- Install the required packages

    ```python
    pip install -r requirements.txt
    ```

## Run the application

- Run the application

    ```python
    python .\src\main.py
    ```

## Package the application to an executable

- Package the application

```c++
pyinstaller --onefile --windowed .\src\main.py
```

- The executable file will be generated in the `dist` folder
