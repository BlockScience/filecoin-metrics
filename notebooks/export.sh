# Make sure that we have a clean output/ sub folder
rm -rf output/

INPUT_NOTEBOOK=sector_state_before_upgrade.ipynb
OUTPUT_DIR=output

# Export to markdown

# Export to PDF through headless browser rendering

# Export to HTML
jupyter nbconvert --to html --template full $INPUT_NOTEBOOK --output-dir $OUTPUT_DIR
