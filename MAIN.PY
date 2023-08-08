import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime, timedelta
import sqlite3
from tkcalendar import DateEntry
from ttkthemes import ThemedTk


class ProductApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de Productos")
        
        self.root.attributes('-fullscreen', True)
        
        self.create_widgets()
        
        self.connect_to_db()
    
    def connect_to_db(self):
        self.conn = sqlite3.connect('product_db.sqlite')
        self.cursor = self.conn.cursor()
        self.create_table()
    
    def create_table(self):
        query = '''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            product TEXT,
            lot TEXT,
            expiration DATE
        )
        '''
        self.cursor.execute(query)
        self.conn.commit()
    
    def create_widgets(self):
        # Panel para agregar productos (a la izquierda)
        add_frame = tk.Frame(self.root)
        add_frame.pack(side="left", padx=20, pady=20, anchor="nw")
        
        self.product_label = tk.Label(add_frame, text="Producto:", font=("Arial", 14))
        self.product_label.pack(pady=(10, 0))
        
        self.product_entry = tk.Entry(add_frame, font=("Arial", 12))
        self.product_entry.pack(pady=(0, 10))
        
        self.lot_label = tk.Label(add_frame, text="Lote:", font=("Arial", 14))
        self.lot_label.pack()
        
        self.lot_entry = tk.Entry(add_frame, font=("Arial", 12))
        self.lot_entry.pack(pady=(0, 10))
        
        self.exp_label = tk.Label(add_frame, text="Vencimiento:", font=("Arial", 14))
        self.exp_label.pack()
        
        self.exp_cal = DateEntry(add_frame, date_pattern='dd-mm-yyyy', font=("Arial", 12))
        self.exp_cal.pack(pady=(0, 10))
        
        self.add_button = tk.Button(add_frame, text="Agregar Producto", command=self.add_product, font=("Arial", 12))
        self.add_button.pack()
        
        # Panel para buscar productos (a la derecha)
        search_frame = tk.Frame(self.root)
        search_frame.pack(side="right", padx=20, pady=20, anchor="ne")
        
        self.search_label = tk.Label(search_frame, text="Buscar Producto:", font=("Arial", 14))
        self.search_label.pack(pady=(10, 0))
        
        self.search_entry = tk.Entry(search_frame, font=("Arial", 12))
        self.search_entry.pack(pady=(0, 10))
        
        self.search_button = tk.Button(search_frame, text="Buscar", command=self.search_product, font=("Arial", 12))
        self.search_button.pack()
        
        # Tabla (ocupa el espacio central)
        self.table_frame = ttk.Frame(self.root)
        self.table_frame.pack(side="top", padx=20, pady=10, fill="both", expand=True)
        
        self.table = ttk.Treeview(self.table_frame, columns=("Producto", "Lote", "Vencimiento"), show="headings", height=15)
        self.table.heading("Producto", text="Producto")
        self.table.heading("Lote", text="Lote")
        self.table.heading("Vencimiento", text="Vencimiento")
        self.table.pack(fill="both", expand=True)
        
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 16), rowheight=40)  # Cambio del tamaño de fuente y altura de fila
        style.configure("Treeview.Heading", font=("Arial", 16))  # Cambio del tamaño de fuente para encabezados
        
        self.table.tag_configure("odd_row", background="#f0f0f0")
        self.table.tag_configure("even_row", background="white")
        self.table.tag_configure("selected_row", background="#0078d7", foreground="white")
        
        # Botones de operaciones (debajo de la sección de búsqueda)
        operations_frame = tk.Frame(self.root)
        operations_frame.pack(side="bottom", padx=20, pady=10, fill="both", anchor="se")
        
        self.edit_button = tk.Button(operations_frame, text="Editar Producto", command=self.edit_product, font=("Arial", 12))
        self.edit_button.pack(side="left", padx=10)
        
        self.delete_button = tk.Button(operations_frame, text="Eliminar Producto", command=self.delete_product, font=("Arial", 12))
        self.delete_button.pack(side="left", padx=10)
        
        self.check_expirations_button = tk.Button(operations_frame, text="Verificar Vencimientos", command=self.check_expirations, font=("Arial", 12))
        self.check_expirations_button.pack(side="left", padx=10)
        
        # Botón para cerrar el programa (esquina inferior derecha)
        close_button = tk.Button(self.root, text="Cerrar", command=self.root.destroy, font=("Arial", 12))
        close_button.pack(side="bottom", padx=20, pady=10, anchor="se")
    
    def add_product(self):
        product = self.product_entry.get()
        lot = self.lot_entry.get()
        exp = self.exp_cal.get_date().strftime('%d-%m-%Y')
        
        query = "INSERT INTO products (product, lot, expiration) VALUES (?, ?, ?)"
        values = (product, lot, exp)
        
        try:
            self.cursor.execute(query, values)
            self.conn.commit()
            self.update_table()
            messagebox.showinfo("Aviso", "Producto agregado exitosamente.")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"No se pudo agregar el producto: {e}")
    
    def update_table(self):
        self.clear_table()
        
        query = "SELECT * FROM products"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        
        for row in rows:
            self.table.insert("", "end", values=(row[1], row[2], row[3]))
    
    def clear_table(self):
        for row in self.table.get_children():
            self.table.delete(row)
    
    def check_expirations(self):
        self.clear_table()
        
        today = datetime.today().date()
        soon = today + timedelta(days=30)
        
        query = "SELECT * FROM products"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        
        for row in rows:
            exp_date = datetime.strptime(row[3], "%d-%m-%Y").date()
            if exp_date < today:
                color = "red"
            elif today <= exp_date <= soon:
                color = "yellow"
            else:
                color = ""
            
            self.table.insert("", "end", values=(row[1], row[2], row[3]), tags=(color,))
            self.table.tag_configure(color, background=color)
    
    def delete_product(self):
        selected_item = self.table.selection()
        
        if not selected_item:
            messagebox.showwarning("Advertencia", "Selecciona un producto para eliminar.")
            return
        
        item = self.table.focus()
        product_idx = self.table.index(item)
        
        query = "SELECT id FROM products"
        self.cursor.execute(query)
        ids = [row[0] for row in self.cursor.fetchall()]
        
        product_id = ids[product_idx]
        
        query = "DELETE FROM products WHERE id = ?"
        values = (product_id,)
        
        try:
            self.cursor.execute(query, values)
            self.conn.commit()
            self.update_table()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"No se pudo eliminar el producto: {e}")
    
    def edit_product(self):
        selected_item = self.table.selection()

        if not selected_item:
            messagebox.showwarning("Advertencia", "Selecciona un producto para editar.")
            return

        item = self.table.focus()
        product_idx = int(self.table.index(item))

        product = self.table.item(item, "values")[0]
        lot = self.table.item(item, "values")[1]
        exp = self.table.item(item, "values")[2]

        self.product_entry.delete(0, tk.END)
        self.product_entry.insert(0, product)

        self.lot_entry.delete(0, tk.END)
        self.lot_entry.insert(0, lot)

        self.exp_cal.delete(0, tk.END)
        self.exp_cal.set_date(datetime.strptime(exp, '%d-%m-%Y'))

        self.delete_product()
        self.update_table()
    
    def search_product(self):
        search_term = self.search_entry.get()
        query = "SELECT * FROM products WHERE product LIKE ? OR lot LIKE ?"
        values = (f"%{search_term}%", f"%{search_term}%")
        self.cursor.execute(query, values)
        rows = self.cursor.fetchall()
        
        self.clear_table()
        
        for row in rows:
            self.table.insert("", "end", values=(row[1], row[2], row[3]))
    
if __name__ == "__main__":
    themed_root = ThemedTk(theme="clam")  # Crea una instancia de ThemedTk con el tema "clam"
    app = ProductApp(themed_root)
    themed_root.mainloop()


