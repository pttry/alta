for %%f in (*.tab) do change32 changes %%f out\%%f
copy out\*.tab .
