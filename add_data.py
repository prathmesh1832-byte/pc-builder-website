from app import app
from models import db, Product

with app.app_context():
    Product.query.delete()   # clear existing products first
    db.session.commit()

    sample_products = [
        Product(name="AMD Ryzen 5 5600", category="CPU", brand="AMD", price=11500,
                stock=10, socket_type="AM4", wattage=65,
                image="amdryzen55600.jpeg"),
        Product(name="Intel Core i5-12400F", category="CPU", brand="Intel", price=13500,
                stock=8, socket_type="LGA1700", wattage=65,
                image="intelcorei512400f.jpeg"),

        Product(name="MSI B450M-A PRO MAX", category="Motherboard", brand="MSI", price=6500,
                stock=6, socket_type="AM4", ram_type="DDR4", form_factor="mATX",
                image="msib450mapromax.jpg"),
        Product(name="ASUS PRIME B660M-A", category="Motherboard", brand="ASUS", price=11000,
                stock=5, socket_type="LGA1700", ram_type="DDR4", form_factor="mATX",
                image="asusprimeb660ma.png"),

        Product(name="Corsair Vengeance 16GB DDR4 3200MHz", category="RAM", brand="Corsair",
                price=3200, stock=15, ram_type="DDR4",
                image="corsairvengeance16gbddr43200mhz.jpeg"),
        Product(name="G.Skill Ripjaws 16GB DDR5 5600MHz", category="RAM", brand="G.Skill",
                price=5200, stock=10, ram_type="DDR5",
                image="gskillripjaws16gbddr55600mhz.jpeg"),

        Product(name="NVIDIA RTX 4060", category="GPU", brand="NVIDIA", price=32000,
                stock=4, wattage=115,
                image="nvidiartx4060.jpeg"),
        Product(name="AMD RX 6600", category="GPU", brand="AMD", price=22000,
                stock=5, wattage=132,
                image="amdrx6600.jpg"),

        Product(name="Corsair 650W 80+ Bronze", category="PSU", brand="Corsair", price=4500,
                stock=10, wattage=650,
                image="corsair650w80bronze.jpeg"),
        Product(name="Cooler Master 750W 80+ Gold", category="PSU", brand="Cooler Master",
                price=6800, stock=7, wattage=750,
                image="coolermaster750w80gold.jpeg"),

        Product(name="Samsung 970 EVO 500GB NVMe SSD", category="Storage", brand="Samsung",
                price=3800, stock=12,
                image="samsung970evo500gbnvmessd.jpeg"),
        Product(name="Seagate Barracuda 1TB HDD", category="Storage", brand="Seagate",
                price=2800, stock=20,
                image="seagatebarracuda1tbhdd.jpeg"),

        Product(name="NZXT H510", category="Case", brand="NZXT", price=5500,
                stock=6, form_factor="ATX",
                image="nzxth510.jpeg"),
        Product(name="Ant Esports ICE-130TG", category="Case", brand="Ant Esports",
                price=2500, stock=9, form_factor="mATX",
                image="antesportsice130tg.jpeg"),
    ]

    db.session.add_all(sample_products)
    db.session.commit()
    print("Sample products refreshed with images!")