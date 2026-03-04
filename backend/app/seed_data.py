"""
Rayeva AI — Seed Data
Realistic sustainable products for testing and demo.
Run: python -m app.seed_data
"""

SAMPLE_PRODUCTS = [
    {
        "name": "Bamboo Cutlery Travel Set",
        "description": "Reusable bamboo utensils including fork, knife, spoon, and chopsticks. Comes in an organic cotton roll-up pouch. Perfect alternative to single-use plastic cutlery. Lightweight and durable for daily use or travel.",
        "price": 349.0,
    },
    {
        "name": "Handmade Coconut Bowl Set",
        "description": "Set of 2 bowls handcrafted from reclaimed coconut shells, polished with virgin coconut oil. Each bowl is unique. Includes wooden spoon. Vegan-friendly, zero waste packaging using recycled cardboard.",
        "price": 599.0,
    },
    {
        "name": "Organic Cotton Tote Bag",
        "description": "100% GOTS certified organic cotton tote bag. Heavy-duty 12oz canvas, reinforced handles. Block-printed by local artisans using natural dyes. Replaces hundreds of single-use plastic bags. Machine washable.",
        "price": 449.0,
    },
    {
        "name": "Beeswax Food Wrap Set",
        "description": "Set of 3 reusable beeswax wraps (small, medium, large). Made with organic cotton, sustainably sourced beeswax, jojoba oil, and tree resin. Replaces plastic cling film. Lasts up to 1 year with care.",
        "price": 499.0,
    },
    {
        "name": "Seed Paper Notebook — A5",
        "description": "Beautiful A5 notebook with covers made from plantable seed paper embedded with wildflower seeds. 80 pages of 100% recycled paper. When done, plant the cover and watch it bloom. Soy-based ink printing.",
        "price": 275.0,
    },
    {
        "name": "Neem Wood Comb",
        "description": "Hand-carved neem wood comb with wide teeth. Anti-static, prevents hair breakage. Neem has natural antibacterial properties. Plastic-free alternative to synthetic combs. Each piece is unique due to natural wood grain.",
        "price": 199.0,
    },
    {
        "name": "Activated Charcoal Soap Bar",
        "description": "Natural activated charcoal face and body soap. Made with coconut oil, shea butter, and activated bamboo charcoal. Detoxifies and deep cleanses. Palm oil free. No synthetic fragrances or preservatives. Handmade in small batches.",
        "price": 175.0,
    },
    {
        "name": "Stainless Steel Water Bottle — 750ml",
        "description": "Double-wall vacuum insulated stainless steel bottle. Keeps drinks cold for 24 hours and hot for 12 hours. BPA-free, no plastic components. Powder-coated finish with bamboo cap. Replaces 150+ plastic bottles per year.",
        "price": 899.0,
    },
    {
        "name": "Jute Yoga Mat Bag",
        "description": "Handwoven jute yoga mat carrier bag with adjustable cotton strap. Fits mats up to 6mm thick. Interior pocket for keys and phone. Made by women's self-help group in West Bengal. Naturally biodegradable.",
        "price": 649.0,
    },
    {
        "name": "Organic Herbal Tea Gift Box",
        "description": "Curated box of 4 organic loose-leaf teas: chamomile, tulsi green, lemongrass ginger, and masala chai. Sourced from small-scale organic farms in Darjeeling and Assam. Plastic-free packaging in reusable tin.",
        "price": 749.0,
    },
    {
        "name": "Recycled Newspaper Pencils — Set of 10",
        "description": "HB pencils made from 100% recycled newspaper. Each pencil has a plantable flower seed tip. Non-toxic, safe for children. Manufactured by a social enterprise employing differently-abled workers. Zero wood used.",
        "price": 120.0,
    },
    {
        "name": "Cork Desk Organizer",
        "description": "Minimalist desk organizer made from sustainable Portuguese cork. 4 compartments for pens, cards, and stationery. Cork is harvested without cutting trees. Lightweight, water-resistant, and naturally antimicrobial.",
        "price": 1299.0,
    },
    {
        "name": "Biodegradable Phone Case",
        "description": "Phone case made from plant-based bioplastic (PLA) and bamboo fiber composite. Fully compostable in industrial composting facilities. Drop protection up to 6 feet. Available for iPhone and Samsung models. Minimalist design.",
        "price": 799.0,
    },
    {
        "name": "Loofah Kitchen Sponge — Pack of 3",
        "description": "Natural loofah (luffa gourd) kitchen sponges. Grown organically, dried and cut to sponge size. Completely plastic-free alternative to synthetic kitchen sponges. Biodegradable. Lasts 4-6 weeks. Compostable after use.",
        "price": 149.0,
    },
    {
        "name": "Upcycled Denim Laptop Sleeve",
        "description": "Laptop sleeve handcrafted from upcycled denim jeans. Padded with organic cotton batting for protection. Fits 13-14 inch laptops. Each piece is one-of-a-kind with unique denim textures and stitching. Handmade by rural artisans.",
        "price": 999.0,
    },
    {
        "name": "Clay Water Bottle — Terracotta",
        "description": "Traditional terracotta clay water bottle with natural cooling properties. Handmade by potters in Rajasthan. Keeps water naturally cool without electricity. Food-grade clay, no chemicals or glazes. Includes cork stopper.",
        "price": 399.0,
    },
    {
        "name": "Hemp Protein Bar — Pack of 6",
        "description": "Vegan protein bars made with Indian hemp seeds, organic dates, almonds, and cacao. 15g plant protein per bar. No refined sugar, no preservatives. Gluten-free. Wrapped in compostable cellulose packaging.",
        "price": 540.0,
    },
    {
        "name": "Brass Reusable Straw Set",
        "description": "Set of 4 brass drinking straws with cleaning brush. Kansa (bronze) alloy has natural purifying properties in Ayurveda. Handcrafted by metalsmith artisans. Replaces thousands of single-use plastic straws. Comes in cotton pouch.",
        "price": 450.0,
    },
    {
        "name": "Organic Baby Romper — 0-6 months",
        "description": "GOTS certified organic cotton baby romper. Naturally dyed with turmeric and indigo. Nickel-free snap buttons. Gentle on sensitive baby skin with no synthetic chemicals. Made in a fair-trade certified facility.",
        "price": 699.0,
    },
    {
        "name": "Compostable Bin Liners — Roll of 30",
        "description": "100% compostable trash bags made from corn starch (PLA). Certified to EN 13432 standard. 19L capacity, suitable for kitchen compost bins. Breaks down in 90 days in industrial composting. No microplastics.",
        "price": 249.0,
    },
]


def seed_products():
    """Insert sample products into the database (for testing, not categorized yet)."""
    from app.database import SessionLocal, init_db
    from app.models.product import Product

    init_db()
    db = SessionLocal()
    try:
        existing = db.query(Product).count()
        if existing > 0:
            print(f"Database already has {existing} products. Skipping seed.")
            return

        for data in SAMPLE_PRODUCTS:
            product = Product(
                name=data["name"],
                description=data["description"],
                price=data["price"],
            )
            db.add(product)
        db.commit()
        print(f"Seeded {len(SAMPLE_PRODUCTS)} sample products.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_products()
