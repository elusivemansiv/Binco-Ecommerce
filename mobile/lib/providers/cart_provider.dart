import 'package:flutter/foundation.dart';
import '../services/api_service.dart';

class CartItem {
  final int id;
  final int productId;
  final String productName;
  final double price;
  final int quantity;
  final String? image;

  CartItem({
    required this.id,
    required this.productId,
    required this.productName,
    required this.price,
    required this.quantity,
    this.image,
  });

  factory CartItem.fromJson(Map<String, dynamic> json) {
    return CartItem(
      id: json['id'],
      productId: json['product']?['id'] ?? 0,
      productName: json['product']?['name'] ?? 'Unknown',
      price: double.tryParse(json['price']?.toString() ?? '0') ?? 0.0,
      quantity: json['quantity'] ?? 1,
      image: json['product']?['image'],
    );
  }
}

class CartProvider with ChangeNotifier {
  final ApiService _apiService = ApiService();
  
  List<CartItem> _items = [];
  bool _isLoading = false;

  List<CartItem> get items => _items;
  bool get isLoading => _isLoading;
  
  double get totalAmount {
    return _items.fold(0.0, (sum, item) => sum + (item.price * item.quantity));
  }
  
  int get itemCount {
    return _items.fold(0, (sum, item) => sum + item.quantity);
  }

  Future<void> fetchCart() async {
    try {
      _isLoading = true;
      notifyListeners();

      final response = await _apiService.get('/cart/');
      if (response != null && response['items'] != null) {
        final List data = response['items'];
        _items = data.map((json) => CartItem.fromJson(json)).toList();
      } else {
        _items = [];
      }
    } catch (e) {
      print('Error fetching cart: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> addToCart(int productId, int quantity) async {
    try {
      _isLoading = true;
      notifyListeners();

      await _apiService.post('/cart/add/', {
        'product_id': productId,
        'quantity': quantity,
      });

      await fetchCart();
      return true;
    } catch (e) {
      print('Error adding to cart: $e');
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }
}
