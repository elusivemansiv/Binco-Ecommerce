class Product {
  final int id;
  final String name;
  final String slug;
  final String? image;
  final double price;
  final double discountPrice;
  final int discountPercent;
  final String categoryName;
  final bool inStock;

  Product({
    required this.id,
    required this.name,
    required this.slug,
    this.image,
    required this.price,
    required this.discountPrice,
    required this.discountPercent,
    required this.categoryName,
    required this.inStock,
  });

  factory Product.fromJson(Map<String, dynamic> json) {
    return Product(
      id: json['id'],
      name: json['name'],
      slug: json['slug'],
      image: json['image'],
      price: double.tryParse(json['price']?.toString() ?? '0') ?? 0.0,
      discountPrice: double.tryParse(json['discount_price']?.toString() ?? '0') ?? 0.0,
      discountPercent: json['discount_percent'] ?? 0,
      categoryName: json['category_name'] ?? 'Uncategorized',
      inStock: json['in_stock'] ?? true,
    );
  }
}
