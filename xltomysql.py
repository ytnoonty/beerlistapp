import xlrd
import MySQLdb

# Open the workbook and define the worksheet
book = xlrd.open_workbook("BeerList.xls")
sheet = book.sheet_by_name("beerlistSheet")

# Establish a MySQL connection
database = MySQLdb.connect (host="localhost", user="root", passwd="qwerty", db="myflaskapp")

# Get the cursor, which is used to traverse the database, line by line
cursor = database.cursor()

# Create the INSERT INTO sql query
query = """INSERT INTO beerlist_main(name, style, abv, ibu, brewery, location, website, description) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)"""
# Create a For loop to itereate through each row in the XLS file, starting at row 2 to skip the headers
for r in range(0, 219):#sheet.nrows):
    name = sheet.cell(r,0).value
    style = sheet.cell(r,1).value
    abv = sheet.cell(r,2).value
    ibu = sheet.cell(r,3).value
    brewery = sheet.cell(r,4).value
    location = sheet.cell(r,5).value
    website = sheet.cell(r,6).value
    description = sheet.cell(r,7).value

# Assign values from each row
    values = (name, style, abv, ibu, brewery, location, website, description)

# Execute sql query
    cursor.execute(query, values)

# Close the cursor
cursor.close()

# Commit the transaction
database.commit()

# Close the database connection
database.close()

# Print results
print ""
print "All Done! But, for now."
print ""
columns = str(sheet.ncols)
rows = str(sheet.nrows)
print "just imported " + columns + " columns and " + rows + " rows to MySQL!"
