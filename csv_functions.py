  
import csv

def generate_csv_books(array_of_books, file_name):
  try:
    file_results = open(file_name, 'w')
    writer = csv.writer(file_results)
    writer.writerow(list( array_of_books[0].keys()))
    for dictionary in array_of_books:
        writer.writerow(dictionary.values())
    file_results.close()
  except Exception as e:
    print("Error en la funcion generate_csv_books")
    print(array_of_books)
    print(file_name)
    print("Error en la funcion generate_csv_books")
    print(e)  