from matplotlib import pyplot as plt

from son import CarbonCalculator, Household, Personal, Business
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class CarbonCalculatorGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Karbon Ayak İzi Hesaplayıcı")
        self.root.geometry("800x600")

        self.calculator = CarbonCalculator()

        # Main container
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Calculator type selection
        ttk.Label(self.main_frame, text="Hesaplayıcı Türü").pack(pady=5)
        self.calc_type = ttk.Combobox(self.main_frame, values=["Bireysel", "Kurumsal"])
        self.calc_type.set("Bireysel")
        self.calc_type.pack(pady=5)
        self.calc_type.bind('<<ComboboxSelected>>', self.on_type_change)

        # Start calculation button
        ttk.Button(self.main_frame, text="Hesaplamaya Başla", command=self.start_calculation).pack(pady=10)

        self.car_frames = []  # To keep track of car entry frames

    def on_type_change(self, event):
        # Reset calculator when type changes
        self.calculator = CarbonCalculator()

    def start_calculation(self):
        if self.calc_type.get() == "Bireysel":
            self.calculator.calculator_type = 'individual'
            self.collect_individual_data()
        else:
            self.calculator.calculator_type = 'business'
            self.collect_business_data()

    def collect_individual_data(self):
        data_window = tk.Toplevel(self.root)
        data_window.title("Bireysel Veri Girişi")
        data_window.geometry("800x800")

        # Create scrollable frame
        canvas = tk.Canvas(data_window)
        scrollbar = ttk.Scrollbar(data_window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        def create_entry(label):
            ttk.Label(scrollable_frame, text=label).pack()
            entry = ttk.Entry(scrollable_frame)
            entry.pack(pady=5)
            return entry

        def create_checkbox(label):
            var = tk.BooleanVar()
            ttk.Checkbutton(scrollable_frame, text=label, variable=var).pack(pady=5)
            return var

        def create_combobox(label, values):
            ttk.Label(scrollable_frame, text=label).pack()
            combo = ttk.Combobox(scrollable_frame, values=values, state="readonly")
            combo.pack(pady=5)
            combo.set(values[0])  # Set default value
            return combo

        # Household Section
        ttk.Label(scrollable_frame, text="Hane Bilgileri", font=('Arial', 12, 'bold')).pack(pady=10)
        members_entry = create_entry("Hane halkı sayısı:")
        electricity_entry = create_entry("Yıllık elektrik tüketimi (kWh):")
        green_electricity = create_checkbox("Yeşil elektrik tarifesi")
        gas_entry = create_entry("Yıllık doğalgaz tüketimi (kWh):")
        other_heating = create_checkbox("Diğer ısıtma yöntemi")

        # Car section
        car_section = ttk.LabelFrame(scrollable_frame, text="Araç Bilgileri")
        car_section.pack(fill='x', padx=5, pady=5)

        def update_car_frames(*args):
        # Clear existing car frames
            for car_data in self.car_frames:
                car_data['frame'].destroy()  # Destroy the frame from the dictionary
            self.car_frames.clear()
        
            try:
                num_cars = int(cars_entry.get())
                if 0 <= num_cars <= 4:  # Limit to reasonable number
                    for i in range(num_cars):
                        car_frame = ttk.LabelFrame(car_section, text=f"Araç {i+1}")
                        car_frame.pack(fill='x', padx=5, pady=5)
                    
                        # Car type dropdown
                        ttk.Label(car_frame, text="Araç tipi:").pack()
                        car_type = ttk.Combobox(car_frame, values=["küçük", "orta", "büyük"], state="readonly")
                        car_type.pack(pady=5)
                        car_type.set("orta")  # default value
                    
                        # Mileage entry
                        ttk.Label(car_frame, text="Yıllık kilometre:").pack()
                        mileage_entry = ttk.Entry(car_frame)
                        mileage_entry.pack(pady=5)
                    
                        self.car_frames.append({
                            'frame': car_frame, 
                            'type': car_type, 
                            'mileage': mileage_entry
                        })
                else:
                    messagebox.showerror("Hata", "Araç sayısı 0-4 arasında olmalıdır")
                    cars_entry.delete(0, tk.END)
                    cars_entry.insert(0, "0")
            except ValueError:
                pass

        ttk.Label(car_section, text="Araç sayısı (0-4):").pack()
        cars_entry = ttk.Entry(car_section)
        cars_entry.pack(pady=5)
        cars_entry.bind('<KeyRelease>', update_car_frames)

        # Food Section
        food_frame = ttk.LabelFrame(scrollable_frame, text="Gıda Tercihleri")
        food_frame.pack(fill='x', padx=5, pady=5)

        organic_food = create_combobox("Gıdalarınızın ne kadarı organik?",
                                       ["Hiçbiri", "Bazıları", "Çoğu", "Hepsi"])

        meat_dairy = create_combobox("Et/süt tüketiminiz nedir?",
                                     ["Ortalamanın üstünde et/süt", "Ortalama et/süt",
                                      "Ortalamanın altında et/süt", "Lakto-vejetaryen", "Vegan"])

        local_food = create_combobox("Gıdalarınızın ne kadarı yerel olarak üretiliyor?",
                                     ["Çok azı", "Ortalama", "Ortalamanın üzerinde", "Tamamı"])

        processed_food = create_combobox("Gıdalarınızın ne kadarı paketli/işlenmiş?",
                                         ["Ortalamanın üzerinde", "Ortalama", "Ortalamanın altında", "Çok az"])

        composting = create_combobox("Ne sıklıkla kompost yapıyorsunuz?",
                                     ["Hiç", "Bazen", "Her zaman"])

        food_waste = create_combobox("Ne kadar gıda israf ediyorsunuz?",
                                     ["Ortalamanın üzerinde(50% çok)", "Ortalama",
                                      "Ortalamanın altında (50% az)", "Çok az (90% az)"])

        # Transportation Section
        transport_frame = ttk.LabelFrame(scrollable_frame, text="Ulaşım")
        transport_frame.pack(fill='x', padx=5, pady=5)

        bus_miles = create_entry("Yıllık otobüs kilometresi:")
        train_miles = create_entry("Yıllık tren kilometresi:")
        flight_hours = create_entry("Yıllık uçuş saati:")

        # Lifestyle and Spending Section
        lifestyle_frame = ttk.LabelFrame(scrollable_frame, text="Yaşam Tarzı ve Harcamalar")
        lifestyle_frame.pack(fill='x', padx=5, pady=5)

        spending = create_combobox("Diğer harcamalarınız ne seviyede?",
                                   ["Ortalamanın Üstünde (5 ton CO2)",
                                    "Ortalama (3.4 ton CO2)",
                                    "Ortalamanın Altında (2.4 ton CO2)",
                                    "Ortalamanın Çok Altında (1.4 ton CO2)"])

        recycles_basic = create_checkbox("Kağıt, cam ve metali geri dönüştürüyor musunuz?")
        recycles_plastic = create_checkbox("Poşetler dışında plastiği geri dönüştürüyor musunuz?")

        def collect_and_calculate():
            try:
                # Get car data
                car_mileages = {}
                for i, car_frame in enumerate(self.car_frames):
                    car_mileages[f'car_{i + 1}'] = {
                        'type': car_frame['type'].get(),
                        'mileage': float(car_frame['mileage'].get())
                    }

                # Create Household object
                household_data = {
                    'members': float(members_entry.get()),
                    'electricity_kwh': float(electricity_entry.get()),
                    'electricity_green': green_electricity.get(),
                    'gas_kwh': float(gas_entry.get()),
                    'other_heating': other_heating.get(),
                    'num_cars': len(self.car_frames),
                    'car_mileages': car_mileages
                }
                self.calculator.household = Household(**household_data)

                # Create Personal object with all data
                personal_data = {
                    'organic_food': organic_food.get(),
                    'meat_dairy': meat_dairy.get(),
                    'local_food': local_food.get(),
                    'processed_food': processed_food.get(),
                    'composting': composting.get(),
                    'food_waste': food_waste.get(),
                    'bus_miles': float(bus_miles.get() or 0),
                    'train_miles': float(train_miles.get() or 0),
                    'flight_hours': float(flight_hours.get() or 0),
                    'spending': spending.get(),
                    'recycles_basic': recycles_basic.get(),
                    'recycles_plastic': recycles_plastic.get()
                }
                self.calculator.personal = Personal(**personal_data)

                # Calculate and display results
                self.display_results()
                data_window.destroy()

            except ValueError as e:
                messagebox.showerror("Hata", f"Lütfen tüm alanları doğru formatta doldurun: {str(e)}")

        ttk.Button(scrollable_frame, text="Hesapla", command=collect_and_calculate).pack(pady=20)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def collect_business_data(self):
        # collect_individual_data but for business
        data_window = tk.Toplevel(self.root)
        data_window.title("Kurumsal Veri Girişi")
        data_window.geometry("600x800")

        # Create scrollable frame
        canvas = tk.Canvas(data_window)
        scrollbar = ttk.Scrollbar(data_window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        def create_entry(label):
            ttk.Label(scrollable_frame, text=label).pack()
            entry = ttk.Entry(scrollable_frame)
            entry.pack(pady=5)
            return entry

        # Business data entries
        ttk.Label(scrollable_frame, text="İşletme Bilgileri", font=('Arial', 12, 'bold')).pack(pady=10)
        name_entry = create_entry("İşletme adı:")
        sector_combo = ttk.Combobox(scrollable_frame, values=list(self.calculator.SECTOR_MULTIPLIERS.keys()))
        sector_combo.pack(pady=5)
        employees_entry = create_entry("Çalışan sayısı:")
        space_entry = create_entry("Ofis alanı (m²):")
        electricity_entry = create_entry("Yıllık elektrik tüketimi (kWh):")
        gas_entry = create_entry("Yıllık doğalgaz tüketimi (kWh):")

        def collect_and_calculate():
            try:
                # Create Business object
                business_data = {
                    'name': name_entry.get(),
                    'sector': sector_combo.get(),
                    'num_employees': int(employees_entry.get()),
                    'office_space_sqft': float(space_entry.get()),
                    'electricity_kwh': float(electricity_entry.get()),
                    'electricity_green': False,
                    'gas_kwh': float(gas_entry.get()),
                    'company_vehicles': {},
                    'air_travel_hours': 0,
                    'waste_recycling_rate': 0,
                    'data_center_usage': 0,
                    'supply_chain_assessment': "Temel değerlendirme",
                    'renewable_energy_percent': 0
                }
                self.calculator.business = Business(**business_data)

                # Calculate and display results
                self.display_results()
                data_window.destroy()

            except ValueError as e:
                messagebox.showerror("Hata", f"Lütfen tüm alanları doğru formatta doldurun: {str(e)}")

        ttk.Button(scrollable_frame, text="Hesapla", command=collect_and_calculate).pack(pady=20)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def display_results(self):
        results_window = tk.Toplevel(self.root)
        results_window.title("Sonuçlar")
        results_window.geometry("1500x1200")

        if self.calculator.calculator_type == 'individual':
            total = self.calculator.calculate_total_emissions()
            analysis = self.calculator.analyze_individual_emissions()

            # Text results
            text_frame = ttk.Frame(results_window)
            text_frame.pack(fill='x', padx=10, pady=10)

            text = f"Toplam yıllık emisyonlar: {total:.1f} ton CO2e\n\n"
            text += "Kategoriye göre dağılım:\n"
            for category, emission in analysis['emissions'].items():
                percentage = analysis['percentages'][category]
                text += f"{category}: {emission:.1f} ton CO2e (%{percentage:.1f})\n"

            ttk.Label(text_frame, text=text, justify='left').pack(pady=10)

            # Create frame for graphs
            graphs_frame = ttk.Frame(results_window)
            graphs_frame.pack(fill='both', expand=True, padx=10, pady=10)

            # Pie chart
            pie_frame = ttk.LabelFrame(graphs_frame, text="Emisyon Dağılımı")
            pie_frame.pack(side='left', fill='both', expand=True, padx=5)

            fig1, ax1 = plt.subplots(figsize=(6, 6))
            labels = list(analysis['emissions'].keys())
            sizes = [analysis['emissions'][key] for key in labels]
            ax1.pie(sizes, labels=labels, autopct='%1.1f%%')
            ax1.axis('equal')

            canvas1 = FigureCanvasTkAgg(fig1, master=pie_frame)
            canvas1.draw()
            canvas1.get_tk_widget().pack(fill='both', expand=True)

            # Bar chart
            bar_frame = ttk.LabelFrame(graphs_frame, text="Karbon Ayak İzi Karşılaştırması")
            bar_frame.pack(side='right', fill='both', expand=True, padx=5)

            fig2, ax2 = plt.subplots(figsize=(6, 6))

            # Get comparison data
            combined_df = self.calculator.load_comparison_data()
            if combined_df is not None:
                countries = combined_df['Konum'].tolist()
                co2_values = combined_df['CO2'].tolist()

                # Add user's value
                countries.append('Sizin Ayak İziniz')
                co2_values.append(total)

                # Create bar chart
                bars = ax2.bar(range(len(countries)), co2_values)

                # Highlight user's bar
                bars[-1].set_color('red')

                ax2.set_xticks(range(len(countries)))
                ax2.set_xticklabels(countries, rotation=45, ha='right')
                ax2.set_ylabel('Karbon Ayak İzi (ton CO2e)')
                plt.tight_layout()

                canvas2 = FigureCanvasTkAgg(fig2, master=bar_frame)
                canvas2.draw()
                canvas2.get_tk_widget().pack(fill='both', expand=True)

        else:  # Business
            emissions = self.calculator.calculate_business_emissions()
            text = f"İşletme: {self.calculator.business.name}\n"
            text += f"Sektör: {self.calculator.business.sector}\n\n"
            text += "Emisyonlar:\n"
            for category, value in emissions.items():
                if category != 'toplam':
                    text += f"{category}: {value:.1f} ton CO2e\n"
            text += f"\nToplam emisyonlar: {emissions['toplam']:.1f} ton CO2e"

            ttk.Label(results_window, text=text, justify='left').pack(pady=10)

        # Add export button
        ttk.Button(results_window, text="Rapor Oluştur",
                   command=lambda: self.calculator.generate_report(
                       emissions if self.calculator.calculator_type == 'business' else None)
                   ).pack(pady=10)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = CarbonCalculatorGUI()
    app.run()
