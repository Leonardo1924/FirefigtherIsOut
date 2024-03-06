import tkinter as tk
from tkinter import messagebox, ttk
from ttkwidgets.autocomplete import AutocompleteCombobox
import pandas as pd
from PIL import ImageTk, Image
from datetime import datetime

class SaidasRegistradasWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Saídas Registradas")
        
        self.saidas_frame = tk.Frame(self.root)
        self.saidas_frame.pack(fill=tk.BOTH, expand=True)

        self.saidas_label = tk.Label(self.saidas_frame, text="Saídas registradas:", font=("Arial Black", 25))
        self.saidas_label.pack()

        self.saidas_listbox = tk.Listbox(self.saidas_frame, font=("Arial", 20))
        self.saidas_listbox.pack(fill=tk.BOTH, expand=True)

    def update_saidas_list(self, registros_saida):
        self.saidas_listbox.delete(0, tk.END)
        for registro in registros_saida:
            carro = registro['carro']
            bombeiros = ', '.join(registro['bombeiros'])
            hora_registro = registro['hora_registro']
            self.saidas_listbox.insert(tk.END, f"{carro}, Bombeiros: {bombeiros} - Hora de saída: {hora_registro}")

class RegistoCarrosBombeirosApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Registo de Saída de Carros de Bombeiros")

        self.logo = Image.open("logo.png")
        self.logo = self.logo.resize((200, 200))
        self.logo = ImageTk.PhotoImage(self.logo)

        self.root.resizable(True, True)

        self.carros = self.parse_cars_file()
        self.bombeiros = self.parse_firefighters_file()

        self.registros_saida = []

        self.selected_car = tk.StringVar()
        self.selected_bombeiros = []

        self.saidas_window = None  # Mantém a referência à janela de saídas registradas

        self.create_widgets()

    def parse_firefighters_file(self):
        firefighters_df = pd.read_excel('firefighters.xls')
        firefighters_df['Cod.'] = firefighters_df['Cod.'].astype(str)
        self.firefighters_df = firefighters_df
        return [f"{row['Cod.']}. {row['Nome']}" for index, row in firefighters_df.iterrows()]

    def parse_cars_file(self):
        cars_df = pd.read_excel('cars.xls')
        cars_df['Cod.'] = cars_df['Cod.'].astype(str)
        cars_df = cars_df.sort_values(by='Cod.')
        return [row['Classe'] for index, row in cars_df.iterrows()]

    def create_widgets(self):
        toolbar = ttk.Frame(self.root)
        toolbar.pack(side="top", fill="x")

        image_frame = ttk.Frame(self.root)
        image_frame.pack()

        tk.Label(image_frame, image=self.logo).grid(row=0, column=1, padx=0, pady=0)

        ########################## Frame para Selecionar o Carro: #####################
        frame_car_combobox = tk.Frame(self.root)
        frame_car_combobox.pack()

        tk.Label(frame_car_combobox, text="Selecione o carro:").pack(side="left")

        self.car_combobox = AutocompleteCombobox(frame_car_combobox, width=45)
        self.car_combobox['values'] = self.carros
        self.car_combobox.pack(side="left", padx=10, pady=5)
        
        self.car_combobox.bind("<Return>", lambda event: self.add_car())
        self.car_combobox.bind("<Right>", lambda event: self.autocomplete_car())

        ############################# Selecionar Bombeiros ###############
        frame_combobox_button = tk.Frame(self.root)
        frame_combobox_button.pack()

        tk.Label(frame_combobox_button, text="Selecione os bombeiros:").grid(row=0, column=0)

        self.bombeiro_dropdown = AutocompleteCombobox(frame_combobox_button, width=45)
        self.bombeiro_dropdown.set_completion_list(self.bombeiros)
        self.bombeiro_dropdown['values'] = self.bombeiros
        self.bombeiro_dropdown.grid(row=0, column=1, padx=10, pady=5)

        self.bombeiro_dropdown.bind("<Right>", lambda event: self.autocomplete())
        self.bombeiro_dropdown.bind("<Delete>", lambda event: self.clear_bombeiro_dropdown())
        self.bombeiro_dropdown.bind("<Return>", lambda event: self.add_bombeiro())
        

        frame_selected_bombeiros = tk.Frame(self.root)
        frame_selected_bombeiros.pack()

        tk.Label(frame_selected_bombeiros, text="Bombeiros selecionados:").pack(side="left")

        self.bombeiros_selected_listbox = tk.Listbox(frame_selected_bombeiros, selectmode=tk.MULTIPLE, width=40)
        self.bombeiros_selected_listbox.pack(side="left", fill="both", expand=True)

        self.bombeiros_selected_listbox.bind("<Delete>", lambda event: self.remove_bombeiro())
        self.bombeiros_selected_listbox.bind("<BackSpace>", lambda event: self.remove_bombeiro())
        self.bombeiros_selected_listbox.bind("<Return>", lambda event: self.registar_saida())

        self.saidas_frame = tk.Frame(self.root)
        self.saidas_frame.pack(fill=tk.BOTH, expand=True)

        self.saidas_label = tk.Label(self.saidas_frame, text="Saídas registadas:", font=("Arial Black", 25))
        self.saidas_label.pack()

        self.saidas_listbox = tk.Listbox(self.saidas_frame, font=("Arial", 20))
        self.saidas_listbox.pack(fill=tk.BOTH, expand=True)

        self.saidas_listbox.bind("<Delete>", lambda event: self.remover_saida())
        self.saidas_listbox.bind("<BackSpace>", lambda event: self.remover_saida())

        # Botão para abrir a janela de saídas registradas
        show_saidas_button = ttk.Button(toolbar, text="Mostrar Saídas", command=self.show_saidas_window)
        show_saidas_button.pack(side="left")

    def add_car(self):
        car = self.car_combobox.get()
        if car:
            self.selected_car.set(car)

    def autocomplete_car(self):
        text = self.car_combobox.get()
        if text:
            matches = [car for car in self.carros if car.lower().startswith(text.lower())]
            if matches:
                match = matches[0]
                self.car_combobox.set(match)
                self.car_combobox.selection_range(len(text), tk.END)

    def add_bombeiro(self, event=None):
        bombeiro = self.bombeiro_dropdown.get()
        if bombeiro:
            matches = [f"{row['Cod.']}. {row['Nome']}" for index, row in self.firefighters_df.iterrows()]
            if bombeiro in matches:
                if bombeiro not in self.selected_bombeiros:
                    self.selected_bombeiros.append(bombeiro)
                    self.update_bombeiros_selected_listbox()
                    self.clear_bombeiro_dropdown()
                    self.add_car()
            else:
                messagebox.showerror("Erro", "Bombeiro inválido. Por favor, selecione um bombeiro válido.")
                self.clear_bombeiro_dropdown()
                return


    def update_bombeiros_selected_listbox(self):
        self.bombeiros_selected_listbox.delete(0, tk.END)
        for bombeiro in self.selected_bombeiros:
            self.bombeiros_selected_listbox.insert(tk.END, bombeiro)

    def clear_bombeiro_dropdown(self):
        self.bombeiro_dropdown.set("")

    def remove_bombeiro(self):
        selection = self.bombeiros_selected_listbox.curselection()
        if selection:
            self.selected_bombeiros.pop(selection[0])
            self.update_bombeiros_selected_listbox()

    def autocomplete(self, event=None):
        text = self.bombeiro_dropdown.get()
        if text:
            matches = [b for b in self.bombeiros if b.lower().startswith(text.lower())]
            if matches:
                match = matches[0]
                self.bombeiro_dropdown.set(match)
                self.bombeiro_dropdown.selection_range(len(text), tk.END)

    def registar_saida(self):
        # Obter a hora atual
        hora_registro = datetime.now().strftime("%H:%M:%S")

        carro = self.selected_car.get()
        if not carro:
            messagebox.showerror("Erro", "Selecione um carro")
            return

        if carro in [registro['carro'] for registro in self.registros_saida]:
            messagebox.showerror("Erro", "Este veículo já está em uma saída registada")
            return

        for registro in self.registros_saida:
            if any(bombeiro in registro['bombeiros'] for bombeiro in self.selected_bombeiros):
                messagebox.showerror("Erro", "Um dos bombeiros já está em outro carro com saída registada")
                return

        if not self.selected_bombeiros:
            messagebox.showerror("Erro", "Selecione pelo menos um bombeiro")
            return

        registro = {'carro': carro, 'bombeiros': self.selected_bombeiros.copy(), 'hora_registro': hora_registro}
        self.registros_saida.append(registro)

        self.saidas_listbox.insert(tk.END, f"{carro}, Bombeiros:{', '.join(self.selected_bombeiros)} - Hora de saída: {hora_registro}")
        if self.saidas_window:
            self.saidas_window.update_saidas_list(self.registros_saida)  # Atualiza a lista na janela separada

        messagebox.showinfo("Registo de Saída", f"Saída registada:\nCarro: {carro}\nBombeiros: {', '.join(self.selected_bombeiros)}\nHora de Saída: {hora_registro}")
        self.car_combobox.set('')
        self.clear_inputs()

    def clear_inputs(self):
        self.selected_car.set('')
        self.selected_bombeiros.clear()
        self.update_bombeiros_selected_listbox()

    def remover_saida(self):
        selection = self.saidas_listbox.curselection()
        if not selection:
            messagebox.showerror("Erro", "Selecione uma saída para remover")
            return

        self.saidas_listbox.delete(selection[0])
        del self.registros_saida[selection[0]]

        if self.saidas_window:
            self.saidas_window.update_saidas_list(self.registros_saida)  # Atualiza a lista na janela separada

        messagebox.showinfo("Remover Saída", "Saída removida com sucesso")

    def show_saidas_window(self):
        if not self.saidas_window:
            self.saidas_window = tk.Toplevel(self.root)
            self.saidas_window.geometry("800x600")  # Defina o tamanho conforme necessário
            self.saidas_window.resizable(True, True)
            self.saidas_window.title("Saídas Registradas")
            self.saidas_window.protocol("WM_DELETE_WINDOW", self.close_saidas_window)  # Trata o fechamento da janela

            # Cria a instância da janela de saídas registradas
            self.saidas_window_instance = SaidasRegistradasWindow(self.saidas_window)

            # Atualiza a lista na janela separada
            self.saidas_window_instance.update_saidas_list(self.registros_saida)

    def close_saidas_window(self):
        self.saidas_window.destroy()
        self.saidas_window = None

if __name__ == "__main__":
    root = tk.Tk()
    app = RegistoCarrosBombeirosApp(root)
    root.mainloop()

