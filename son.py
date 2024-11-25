from typing import Optional
from dataclasses import dataclass
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt


@dataclass
class Household:
    members: float
    electricity_kwh: float
    electricity_green: bool
    gas_kwh: float
    other_heating: bool
    num_cars: int
    car_mileages: dict[str, dict[str, str | float]]


@dataclass
class Personal:
    organic_food: str
    meat_dairy: str
    local_food: str
    processed_food: str
    composting: str
    food_waste: str
    bus_miles: float
    train_miles: float
    flight_hours: float
    spending: str
    recycles_basic: bool
    recycles_plastic: bool


@dataclass
class Business:
    name: str
    sector: str
    num_employees: int
    office_space_sqft: float
    electricity_kwh: float
    electricity_green: bool
    gas_kwh: float
    company_vehicles: dict[str, dict[str, str | float]]
    air_travel_hours: float
    waste_recycling_rate: float
    data_center_usage: float
    supply_chain_assessment: str
    renewable_energy_percent: float


class CarbonCalculator:
    def __init__(self):
        self.household = None
        self.personal = None
        self.business = None
        self.calculator_type = None

        # Constants for individual calculations
        self.ELECTRICITY_CO2_FACTOR = 0.309  # kg CO2 per kWh
        self.GREEN_ELECTRICITY_REDUCTION = 0.25  # 25% reduction for green tariffs
        self.GAS_CO2_FACTOR = 0.203  # kg CO2 per kWh
        self.CAR_CO2_FACTOR = 14.3  # kg CO2 per gallon

        # Constants for business calculations
        self.OFFICE_SPACE_CO2_FACTOR = 0.05  # tonnes CO2 per sq ft per year
        self.EMPLOYEE_CO2_FACTOR = 2.5  # tonnes CO2 per employee per year
        self.DATA_CENTER_CO2_FACTOR = 0.000475  # tonnes CO2 per kWh

        # Car fuel efficiency (mpg) by type
        self.CAR_MPG = {
            "küçük": 52,
            "orta": 46,
            "büyük": 35
        }

        # Business sectors and their multipliers
        self.SECTOR_MULTIPLIERS = {
            "Teknoloji": 1.0,
            "Üretim": 1.8,
            "Perakende": 1.2,
            "Sağlık": 1.3,
            "Finansal Hizmetler": 0.9,
            "İnşaat": 1.6,
            "Ulaşım": 2.0,
            "Tarım": 1.7,
            "Diğer": 1.0
        }

    def get_calculator_type(self):
        """Kullanılacak hesaplayıcı türünü alır."""
        while True:
            print("\nKarbon Ayak İzi Hesaplayıcı")
            print("1. Bireysel")
            print("2. Kurumsal")
            choice = input("Hesaplayıcı türünü seçin (1/2): ")
            if choice in ['1', '2']:
                self.calculator_type = 'individual' if choice == '1' else 'business'
                break
            print("Lütfen 1 veya 2 girin!")

    def get_float_input(self, prompt: str, default: Optional[float] = None) -> float:
        """Get float input from user with validation."""
        while True:
            try:
                value = input(prompt)
                if not value and default is not None:
                    return default
                return float(value)
            except ValueError:
                print("Lütfen geçerli bir sayı girin!")

    def get_yes_no_input(self, prompt: str) -> bool:
        """Get yes/no input from user."""
        while True:
            response = input(f"{prompt} (e/h): ").lower()
            if response in ['e', 'evet']:
                return True
            if response in ['h', 'hayır']:
                return False
            print("Lütfen 'e' veya 'h' girin")

    def get_choice_input(self, prompt: str, options: list) -> str:
        """Get choice from list of options."""
        print(prompt)
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")

        while True:
            try:
                choice = int(input("Seçiminizi girin (1-{}): ".format(len(options))))
                if 1 <= choice <= len(options):
                    return options[choice - 1]
                print("Geçersiz seçim. Lütfen 1 ile {} arasında bir sayı girin.".format(len(options)))
            except ValueError:
                print("Geçersiz girdi. Lütfen bir sayı girin.")

    def collect_household_data(self):
        """Collect household level data."""
        print("\n=== Hane Bilgileri ===")

        members = self.get_float_input("Hane halkınızda kaç kişi var? ")

        # Electricity usage
        electricity_options = ["Küçük ev/daire (3,000 kWh)", "Orta (4,800 kWh)",
                               "Büyük ev (7,000 kWh)", "Yurt (2,000 kWh)",
                               "Gerçek miktarı girin"]
        electricity_choice = self.get_choice_input("Elektrik tüketimini seçin:", electricity_options)

        if "Gerçek miktarı girin" in electricity_choice:
            electricity_kwh = self.get_float_input("Yıllık elektrik tüketiminizi kWh cinsinden girin: ")
        else:
            electricity_kwh = float(electricity_choice.split("(")[1].split(" ")[0].replace(",", ""))

        electricity_green = self.get_yes_no_input("Sertifikalı yeşil elektrik tarifesi kullanıyor musunuz?")

        # Gas usage
        gas_options = ["Küçük ev/daire (12,000 kWh)", "Orta (18,000 kWh)",
                       "Büyük ev (27,000 kWh)", "Yurt (5,000 kWh)",
                       "Gerçek miktarı girin"]
        gas_choice = self.get_choice_input("Doğalgaz tüketimini seçin:", gas_options)

        if "Gerçek miktarı girin" in gas_choice:
            gas_kwh = self.get_float_input("Yıllık doğalgaz tüketiminizi kWh cinsinden girin: ")
        else:
            gas_kwh = float(gas_choice.split("(")[1].split(" ")[0].replace(",", ""))

        other_heating = self.get_yes_no_input("Fuel-oil, kömür, odun veya LPG gibi başka bir ısınma yöntemi kullanıyor musunuz?")

        # Car usage
        num_cars = int(self.get_float_input("Hane halkınızda kaç araç kullanılıyor? (0-4): "))
        car_mileages = {}

        if num_cars > 0:
            car_types = ["küçük", "orta", "büyük"]
            for i in range(num_cars):
                car_type = self.get_choice_input(f"Araç tipini seçin {i + 1}:", car_types)
                mileage = self.get_float_input(f"Aracın yıllık kilometresini girin {i + 1}: ")
                car_mileages[f"car_{i + 1}"] = {"type": car_type, "mileage": mileage}

        self.household = Household(
            members=members,
            electricity_kwh=electricity_kwh,
            electricity_green=electricity_green,
            gas_kwh=gas_kwh,
            other_heating=other_heating,
            num_cars=num_cars,
            car_mileages=car_mileages
        )

    def collect_personal_data(self):
        """Collect personal lifestyle data."""
        print("\n=== Kişisel Bilgiler ===")

        # Food choices
        organic_options = ["Hiçbiri", "Bazıları", "Çoğu", "Hepsi"]
        organic_food = self.get_choice_input("Gıdalarınızın ne kadarı organik?", organic_options)

        meat_dairy_options = ["Ortalamanın üstünde et/süt", "Ortalama et/süt",
                              "Ortalamanın altında et/süt", "Lakto-vejetaryen", "Vegan"]
        meat_dairy = self.get_choice_input("Et/süt tüketiminiz nedir?", meat_dairy_options)

        local_food_options = ["Çok azı", "Ortalama", "Ortalamanın üzerinde", "Tamamı"]
        local_food = self.get_choice_input("Gıdalarınızın ne kadarı yerel olarak üretiliyor?", local_food_options)

        processed_food_options = ["Ortalamanın üzerinde", "Ortalama", "Ortalamanın altında", "Çok az"]
        processed_food = self.get_choice_input("Gıdalarınızın ne kadarı paketli/işlenmiş?", processed_food_options)

        composting_options = ["Hiç", "Bazen", "Her zaman"]
        composting = self.get_choice_input("Ne sıklıkla kompost yapıyorsunuz?", composting_options)

        food_waste_options = ["Ortalamanın üzerinde(50% çok)", "Ortalama",
                              "Ortalamanın altında (50% az)", "Çok az (90% az)"]
        food_waste = self.get_choice_input("Ne kadar gıda israf ediyorsunuz?", food_waste_options)

        # Transportation
        bus_miles = self.get_float_input("Yıllık otobüs yolculuğu mesafenizi km cinsinden girin: ", 0)
        train_miles = self.get_float_input("Yıllık tren yolculuğu mesafenizi km cinsinden girin: ", 0)
        flight_hours = self.get_float_input("Geçen yılki toplam uçuş saatinizi girin:  ", 0)

        # Lifestyle
        spending_options = ["Ortalamanın Üstünde (5 ton CO2)", "Ortalama (3.4 ton CO2)",
                            "Ortalamanın Altında (2.4 ton CO2)", "Ortalamanın Çok Altında (1.4 ton CO2)"]
        spending = self.get_choice_input("Diğer harcamalarınız ne seviyede?", spending_options)

        recycles_basic = self.get_yes_no_input("Kağıt, cam ve metali geri dönüştürüyor musunuz?")
        recycles_plastic = self.get_yes_no_input("Poşetler dışında plastiği geri dönüştürüyor musunuz?")

        self.personal = Personal(
            organic_food=organic_food,
            meat_dairy=meat_dairy,
            local_food=local_food,
            processed_food=processed_food,
            composting=composting,
            food_waste=food_waste,
            bus_miles=bus_miles,
            train_miles=train_miles,
            flight_hours=flight_hours,
            spending=spending,
            recycles_basic=recycles_basic,
            recycles_plastic=recycles_plastic
        )

    def calculate_household_emissions(self) -> float:
        """Calculate emissions from household energy and car use."""
        if not self.household:
            return 0

        # Electricity emissions
        electricity_emissions = self.household.electricity_kwh * self.ELECTRICITY_CO2_FACTOR
        if self.household.electricity_green:
            electricity_emissions *= (1 - self.GREEN_ELECTRICITY_REDUCTION)

        # Gas emissions
        gas_emissions = self.household.gas_kwh * self.GAS_CO2_FACTOR

        # Car emissions
        car_emissions = 0
        for car in self.household.car_mileages.values():
            mileage_km = car["mileage"] * 1.60934
            mpg = self.CAR_MPG[car["type"]]
            gallons = mileage_km / mpg
            car_emissions += gallons * self.CAR_CO2_FACTOR

        total_household = (electricity_emissions + gas_emissions + car_emissions) / 1000  # Convert to tonnes
        return total_household / self.household.members

    def calculate_personal_emissions(self) -> float:
        """Calculate emissions from personal choices."""
        if not self.personal:
            return 0

        # Food emissions based on choices
        food_emissions = 2.2  # Base food emissions in tonnes

        # Modify based on choices
        food_modifiers = {
            "organic_food": {"Hiçbiri": 1.0, "Bazıları": 0.9, "Çoğu": 0.7, "Hepsi": 0.5},
            "meat_dairy": {"Ortalamanın üstünde et/süt": 1.2, "Ortalama et/süt": 1.0,
                           "Ortalamanın altında et/süt": 0.8, "Lakto-vejetaryen": 0.5, "Vegan": 0.3},
            "local_food": {"Çok azı": 1.2, "Ortalama": 1.0, "Ortalamanın üzerinde": 0.8, "Tamamıl": 0.6},
            "processed_food": {"Ortalamanın üzerinde": 1.2, "Ortalama": 1.0, "Ortalamanın altında": 0.8, "Çok az": 0.6}
        }

        for category, modifiers in food_modifiers.items():
            choice = getattr(self.personal, category)
            food_emissions *= modifiers[choice]

        # Transport emissions
        bus_emissions = self.personal.bus_miles * 0.1 / 1000  # 100g/mile
        train_emissions = self.personal.train_miles * 0.1 / 1000  # 100g/mile
        flight_emissions = self.personal.flight_hours * 0.25  # 0.25 tonnes/hour

        # Spending emissions (already in tonnes)
        spending_emissions = float(self.personal.spending.split("(")[1].split(" ")[0])

        # Public services (constant)
        public_services = 1.1  # tonnes

        return food_emissions + bus_emissions + train_emissions + flight_emissions + spending_emissions + \
            public_services

    def calculate_total_emissions(self) -> float:
        """Calculate total annual emissions."""
        household_emissions = self.calculate_household_emissions()
        personal_emissions = self.calculate_personal_emissions()
        return household_emissions + personal_emissions

    def analyze_individual_emissions(self) -> dict:
        """Analyze emissions by category and compare to averages."""
        if not self.household or not self.personal:
            return {}

        # Calculate emissions by category
        household_energy = (
                (self.household.electricity_kwh * self.ELECTRICITY_CO2_FACTOR *
                 (1 - self.GREEN_ELECTRICITY_REDUCTION if self.household.electricity_green else 1) +
                 self.household.gas_kwh * self.GAS_CO2_FACTOR) / 1000 / self.household.members
        )

        transport = 0
        # Car emissions per person
        for car in self.household.car_mileages.values():
            mpg = self.CAR_MPG[car["type"]]
            gallons = car["mileage"] / mpg
            transport += (gallons * self.CAR_CO2_FACTOR) / 1000 / self.household.members

        # Add public transport
        transport += (self.personal.bus_miles * 0.1 / 1000)  # Bus
        transport += (self.personal.train_miles * 0.1 / 1000)  # Train
        transport += (self.personal.flight_hours * 0.25)  # Flights

        # Food emissions calculation
        food_base = 2.2  # Base food emissions in tonnes
        food_modifiers = {
            "organic_food": {"Hiçbiri": 1.0, "Bazıları": 0.9, "Çoğu": 0.7, "Hepsi": 0.5},
            "meat_dairy": {"Ortalamanın üstünde et/süt": 1.2, "Ortalama et/süt": 1.0,
                           "Ortalamanın altında et/süt": 0.8, "Lakto-vejetaryen": 0.5, "Vegan": 0.3},
            "local_food": {"Çok azı": 1.2, "Ortalama": 1.0, "Ortalamanın üzerinde": 0.8, "Tamamıl": 0.6},
            "processed_food": {"Ortalamanın üzerinde": 1.2, "Ortalama": 1.0, "Ortalamanın altında": 0.8, "Çok az": 0.6}
        }

        food_emissions = food_base
        for category, modifiers in food_modifiers.items():
            choice = getattr(self.personal, category)
            food_emissions *= modifiers[choice]

        # Get spending emissions
        spending = float(self.personal.spending.split("(")[1].split(" ")[0])

        # Public services (constant)
        public_services = 1.1

        # Reference averages (UK)
        averages = {
            "ev_enerjisi": 2.5,
            "ulasim": 3.0,
            "gida": 2.2,
            "harcama": 3.4,
            "kamu_hizmetleri": 1.1
        }

        # Calculate percentages of total
        total = household_energy + transport + food_emissions + spending + public_services
        percentages = {
            "Ev Enerjisi": (household_energy / total) * 100,
            "Ulaşım": (transport / total) * 100,
            "Gıda": (food_emissions / total) * 100,
            "Tüketici Harcaması": (spending / total) * 100,
            "Kamu Hizmetleri": (public_services / total) * 100
        }

        # Compare with averages to identify high-impact areas
        comparison = {
            "Ev Enerjisi": household_energy / averages["ev_enerjisi"],
            "Ulaşım": transport / averages["ulasim"],
            "Gıda": food_emissions / averages["gida"],
            "Tüketici Harcaması": spending / averages["harcama"],
            "Kamu Hizmetleri": 1.0  # Always 1.0 as it's constant
        }

        return {
            "emissions": {
                "Ev Enerjisi": household_energy,
                "Ulaşım": transport,
                "Gıda": food_emissions,
                "Tüketici Harcaması": spending,
                "Kamu Hizmetleri": public_services
            },
            "percentages": percentages,
            "comparison": comparison,
            "averages": averages
        }

    def load_comparison_data(self):
        """Load and combine city and country comparison data with better error handling."""
        try:
            # Read CSV files without specifying usecols to see what columns are actually present
            cities_df = pd.read_csv("Cities.csv")
            countries_df = pd.read_csv("Countries.csv")

            # Select and rename columns based on actual column names
            # Modify these column names to match your actual CSV files
            cities_df = cities_df.iloc[:, [0, 1]]  # Select first two columns
            countries_df = countries_df.iloc[:, [0, 1]]  # Select first two columns

            # Rename columns to match expected format
            cities_df.columns = ['Konum', 'CO2']
            countries_df.columns = ['Konum', 'CO2']

            # Convert CO2 values to numeric, replacing any non-numeric values with NaN
            cities_df['CO2'] = pd.to_numeric(cities_df['CO2'], errors='coerce')
            countries_df['CO2'] = pd.to_numeric(countries_df['CO2'], errors='coerce')

            # Drop any rows with NaN values
            cities_df = cities_df.dropna()
            countries_df = countries_df.dropna()

            # Combine the dataframes
            combined_df = pd.concat([cities_df, countries_df], axis=0)

            return combined_df

        except FileNotFoundError:
            print("Hata: CSV dosyalarından biri veya her ikisi bulunamadı. Lütfen dosya yollarını kontrol edin.")
            return None
        except Exception as e:
            print(f"Karşılaştırma verilerini yüklerken hata oluştu: {str(e)}")
            print("Lütfen CSV dosyalarınızın doğru formatta olduğundan emin olun:")
            print("- En az 2 sütun içermelidir")
            print("-  İlk sütun konum adlarını içermelidir")
            print("-  İkinci sütun CO2 değerlerini içermelidir")
            return None

    def compare_emissions(self, user_emissions, combined_df):
        """Compare user emissions with cities and countries."""
        # Add user's footprint to the dataframe
        combined_df.loc['Sizin Ayak İziniz'] = {'Konum': 'Sizin Ayak İziniz', 'CO2': user_emissions}

        # Sort by location name
        combined_df = combined_df.sort_values('Konum')

        # Print formatted comparison table
        print("\nEmisyon Karşılaştırması (kişi başına ton CO2e):")
        print("-" * 45)
        print(f"{'Konum':<25} {'CO2 Emisyonları':>15}")
        print("-" * 45)

        for index, row in combined_df.iterrows():
            location = row['Konum']
            co2 = row['CO2']

            # Highlight user's footprint
            if location == 'Sizin Ayak İziniz':
                print(f">>> {location:<22} {co2:>15.1f} <<<")
            else:
                print(f"{location:<25} {co2:>15.1f}")

        print("-" * 45)

    def display_results(self):
        """Gelişmiş hesaplama sonuçlarını kategori analiziyle görüntüler."""
        analysis = self.analyze_individual_emissions()
        total = sum(analysis["emissions"].values())

        print("\n=== Karbon Ayak İzi Sonuçlarınız ===")
        print(f"Toplam yıllık emisyonlar: {total:.1f} ton CO2e")

        print("\nKategoriye göre dağılım:")
        print("-" * 50)
        for category, emission in analysis["emissions"].items():
            percentage = analysis["percentages"][category]
            comparison = analysis["comparison"][category]

            print(f"\n{category}:")
            print(f"  Emisyonlar: {emission:.1f} ton CO2e (toplamınızın %{percentage:.1f}'si)")
            print(f"  Birleşik Krallık ortalamasına kıyasla: {comparison:.1f} kat")

            # Kategoriye özgü bilgiler ekleyin
            if comparison > 1.2:  # Ortalamanın %20'sinden fazla
                if category == "Ev Enerjisi":
                    print("  • Enerji verimliliği iyileştirmelerini göz önünde bulundurun")
                    print("  • Yeşil enerji sağlayıcılarına bakın")
                elif category == "Ulaşım":
                    print("  • Araba kullanımını azaltmayı veya elektrikli araçlara geçmeyi düşünün")
                    print("  • Hava yolculuğuna alternatifler arayın")
                elif category == "Gıda":
                    print("  • Et tüketimini azaltmayı düşünün")
                    print("  • Daha fazla yerel ve mevsimlik gıda satın alın")
                elif category == "Tüketici Harcaması":
                    print("  • Tüketimi azaltmanın yollarını arayın")
                    print("  • İkinci el veya tamir seçeneklerini göz önünde bulundurun")
        # İyileştirme için en önemli alanları belirleyin
        high_impact_areas = sorted(
            [(k, v) for k, v in analysis["comparison"].items() if k != "Kamu Hizmetleri"],
            key=lambda x: x[1],
            reverse=True
        )

        print("\nAzaltılması Gereken Öncelikli Alanlar:")
        for area, ratio in high_impact_areas[:2]:
            if ratio > 1:
                print(f"• {area}: Ortalamanın %{(ratio - 1) * 100:.0f} üzerinde")

        combined_df = self.load_comparison_data()
        if combined_df is None:
            return  # CSV dosyaları bulunamadıysa çık

        self.compare_emissions(total, combined_df)

        # Pasta grafiği oluştur
        labels = list(analysis["percentages"].keys())
        sizes = list(analysis["percentages"].values())

        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
        ax.axis('equal')  # Eşit en boy oranı, dairesel pasta grafiği sağlar

        plt.title("Karbon Ayak İzi Dağılımı")
        plt.show()

        # Çubuk grafiği oluştur
        plt.figure(figsize=(10, 6))  # Grafik boyutunu ayarla

        # Ülkelerin ve kullanıcının verilerini al
        countries = combined_df['Konum'].tolist()
        co2_values = combined_df['CO2'].tolist()
        countries.append('Sizin Ayak İziniz')  # Kullanıcıyı ekle
        co2_values.append(total)  # Kullanıcının değerini ekle

        # Çubukları oluştur
        plt.bar(countries, co2_values, color='blue')

        # Kullanıcının çubuğunu vurgula
        plt.bar(countries[-1], co2_values[-1], color='red')

        plt.xlabel("Ülkeler")
        plt.ylabel("Karbon Ayak İzi (ton CO2e)")
        plt.title("Karbon Ayak İzi Karşılaştırması")
        plt.xticks(rotation=45, ha="right")  # Ülke isimlerini döndür
        plt.tight_layout()  # Daha iyi düzen
        plt.show()
        
    def collect_business_data(self):
        """İşletmeyle ilgili verileri toplar."""
        print("\n=== İşletme Bilgileri ===")

        name = input("İşletme adını girin: ")

        # Sektör seçimi
        print("\nİşletme sektörünü seçin:")
        sectors = list(self.SECTOR_MULTIPLIERS.keys())
        sector = self.get_choice_input("İşletme sektörünüzü seçin:", sectors)

        # Temel işletme metrikleri
        num_employees = int(self.get_float_input("Çalışan sayısı: "))
        office_space_sqft = self.get_float_input("Toplam ofis/tesis alanı (metrekare): ")

        # Enerji kullanımı
        electricity_kwh = self.get_float_input("Yıllık elektrik tüketimi (kWh): ")
        electricity_green = self.get_yes_no_input("Yeşil elektrik tarifeleri kullanıyor musunuz?")
        gas_kwh = self.get_float_input("Yıllık doğalgaz tüketimi (kWh): ")

        # Ulaşım
        num_vehicles = int(self.get_float_input("Şirket araç sayısı: ", 0))
        company_vehicles = {}
        if num_vehicles > 0:
            vehicle_types = ["küçük", "orta", "büyük"]
            for i in range(num_vehicles):
                vehicle_type = self.get_choice_input(f"{i + 1}. araç için tipi seçin:", vehicle_types)
                mileage = self.get_float_input(f"{i + 1}. aracın yıllık kilometresini girin: ")
                company_vehicles[f"vehicle_{i + 1}"] = {"type": vehicle_type, "mileage": mileage}

        air_travel_hours = self.get_float_input("Yıllık toplam iş uçuş saatleri: ", 0)

        # Çevresel uygulamalar
        waste_recycling_rate = self.get_float_input("Atık geri dönüşüm oranı (0-100%): ", 0) / 100
        data_center_usage = self.get_float_input("Yıllık veri merkezi enerji kullanımı (kWh): ", 0)

        supply_chain_options = [
            "Değerlendirme yok",
            "Temel değerlendirme",
            "Bazı tedarikçilerle kapsamlı değerlendirme",
            "Tüm tedarikçilerle tam değerlendirme"
        ]
        supply_chain_assessment = self.get_choice_input(
            "Tedarik zinciri çevresel değerlendirme seviyesi:",
            supply_chain_options
        )

        renewable_energy_percent = self.get_float_input("Yenilenebilir kaynaklardan elde edilen enerji yüzdesi (0-100%): ", 0)

        self.business = Business(
            name=name,
            sector=sector,
            num_employees=num_employees,
            office_space_sqft=office_space_sqft,
            electricity_kwh=electricity_kwh,
            electricity_green=electricity_green,
            gas_kwh=gas_kwh,
            company_vehicles=company_vehicles,
            air_travel_hours=air_travel_hours,
            waste_recycling_rate=waste_recycling_rate,
            data_center_usage=data_center_usage,
            supply_chain_assessment=supply_chain_assessment,
            renewable_energy_percent=renewable_energy_percent
        )

    def calculate_business_emissions(self) -> dict:
        """Kategoriye göre işletme karbon emisyonlarını hesaplar."""
        if not self.business:
            return {}

        # Bina emisyonları
        building_emissions = self.business.office_space_sqft * self.OFFICE_SPACE_CO2_FACTOR

        # Enerji emisyonları
        electricity_emissions = (self.business.electricity_kwh * self.ELECTRICITY_CO2_FACTOR / 1000)
        if self.business.electricity_green:
            electricity_emissions *= (1 - self.GREEN_ELECTRICITY_REDUCTION)

        gas_emissions = self.business.gas_kwh * self.GAS_CO2_FACTOR / 1000

        # Araç emisyonları
        vehicle_emissions = 0
        for vehicle in self.business.company_vehicles.values():
            mileage_km = vehicle["mileage"] * 1.60934
            mpg = self.CAR_MPG[vehicle["type"]]
            gallons = mileage_km / mpg
            vehicle_emissions += (gallons * self.CAR_CO2_FACTOR) / 1000

        # Seyahat emisyonları
        air_travel_emissions = self.business.air_travel_hours * 0.25

        # Çalışanla ilgili emisyonlar
        employee_emissions = self.business.num_employees * self.EMPLOYEE_CO2_FACTOR

        # Veri merkezi emisyonları
        data_center_emissions = self.business.data_center_usage * self.DATA_CENTER_CO2_FACTOR

        # Sektör çarpanını uygula
        sector_multiplier = self.SECTOR_MULTIPLIERS[self.business.sector]

        # Yenilenebilir enerji indirimini uygula
        renewable_reduction = self.business.renewable_energy_percent / 100

        # Ayarlamalarla toplamı hesapla
        subtotal = sum([
            building_emissions,
            electricity_emissions,
            gas_emissions,
            vehicle_emissions,
            air_travel_emissions,
            employee_emissions,
            data_center_emissions
        ])

        # Değiştiricileri uygula
        total = subtotal * sector_multiplier * (1 - renewable_reduction)

        return {
            "bina": building_emissions,
            "elektrik": electricity_emissions,
            "dogalgaz": gas_emissions,
            "araclar": vehicle_emissions,
            "hava_yolculugu": air_travel_emissions,
            "calisanlar": employee_emissions,
            "veri_merkezi": data_center_emissions,
            "toplam": total
        }

    def display_business_results(self, emissions: dict):
        """İşletme emisyon sonuçlarını görüntüler."""
        print("\n=== İşletme Karbon Ayak İzi Sonuçları ===")
        print(f"\nSonuçlar: {self.business.name}")
        print(f"Sektör: {self.business.sector}")
        print("\nKategoriye göre emisyonlar (yılda ton CO2e):")
        print(f"Bina operasyonları:        {emissions['bina']:.1f}")
        print(f"Elektrik kullanımı:        {emissions['elektrik']:.1f}")
        print(f"Doğalgaz kullanımı:        {emissions['dogalgaz']:.1f}")
        print(f"Şirket araçları:           {emissions['araclar']:.1f}")
        print(f"İş hava yolculuğu:         {emissions['hava_yolculugu']:.1f}")
        print(f"Çalışanla ilgili:          {emissions['calisanlar']:.1f}")
        print(f"Veri merkezi:              {emissions['veri_merkezi']:.1f}")
        print(f"\nToplam yıllık emisyonlar: {emissions['toplam']:.1f} ton CO2e")

        # Çalışan başına emisyonları hesapla
        per_employee = emissions['toplam'] / self.business.num_employees
        print(f"Çalışan başına emisyonlar: {per_employee:.1f} ton CO2e")

        # Önerilerde bulun
        print("\nAzaltma için öneriler:")
        if emissions['elektrik'] > 50:
            print("- Yenilenebilir enerji kullanımını artırmayı düşünün")
        if emissions['araclar'] > 20:
            print("- Filonuz için elektrikli veya hibrit araçları inceleyin")
        if per_employee > 5:
            print("- Sürdürülebilirlik için çalışan katılım programları uygulayın")
        if emissions['bina'] > 100:
            print("- Bina enerji verimliliği iyileştirmelerine yatırım yapın")
        if emissions['veri_merkezi'] > 10:
            print("- Veri merkezi operasyonlarını optimize edin veya verimli sağlayıcılara geçin")

    def generate_report(self, emissions: dict = None):
        """Karbon ayak izi hesaplamasının ayrıntılı bir raporunu oluşturur."""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"karbon_ayak_izi_raporu_{timestamp}.txt"

        with open(filename, 'w') as f:
            f.write("Karbon Ayak İzi Analiz Raporu\n")
            f.write(f"Oluşturulma Tarihi: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            if self.calculator_type == 'individual':
                total = self.calculate_total_emissions()
                f.write("=== Bireysel Karbon Ayak İzi ===\n")
                f.write(f"Toplam yıllık emisyonlar: {total:.1f} ton CO2e\n")
                f.write("\nOrtalamalarla Karşılaştırma:\n")
                f.write(f"Sizin ayak iziniz: {total:.1f} ton CO2e\n")
                f.write("Dünya ortalaması:  4.4 ton CO2e\n")
                f.write("Birleşik Krallık ortalaması: 14.1 ton CO2e\n")
            else:
                f.write(f"=== İşletme Karbon Ayak İzi: {self.business.name} ===\n")
                f.write(f"Sektör: {self.business.sector}\n")
                f.write("\nKategoriye göre emisyonlar (ton CO2e):\n")
                for category, value in emissions.items():
                    if category != 'toplam':
                        f.write(f"{category.title():15} {value:.1f}\n")
                f.write(f"\nToplam emisyonlar: {emissions['toplam']:.1f} ton CO2e\n")
                f.write(f"Çalışan başına:    {emissions['toplam'] / self.business.num_employees:.1f} ton CO2e\n")

            f.write("\nRapor, Karbon Ayak İzi Hesaplayıcı v1.0 tarafından oluşturuldu")

        print(f"\nAyrıntılı rapor şuraya kaydedildi: {filename}")

    def run(self):
        """Seçilen türe göre hesaplayıcıyı çalıştırır."""
        self.get_calculator_type()

        if self.calculator_type == 'individual':
            self.collect_household_data()
            self.collect_personal_data()
            self.display_results()
            self.generate_report()
        else:
            self.collect_business_data()
            emissions = self.calculate_business_emissions()
            self.display_business_results(emissions)
            self.generate_report(emissions)


def main():
    calculator = CarbonCalculator()
    calculator.run()


if __name__ == "__main__":
    main()
