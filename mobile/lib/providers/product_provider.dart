import 'package:flutter/foundation.dart';
import '../models/product.dart';
import '../services/api_service.dart';

class ProductProvider with ChangeNotifier {
  final ApiService _apiService = ApiService();
  
  List<Product> _featuredProducts = [];
  List<Product> _trendingProducts = [];
  List<dynamic> _categories = [];
  List<dynamic> _sliders = [];
  
  bool _isLoading = false;

  List<Product> get featuredProducts => _featuredProducts;
  List<Product> get trendingProducts => _trendingProducts;
  List<dynamic> get categories => _categories;
  List<dynamic> get sliders => _sliders;
  bool get isLoading => _isLoading;

  Future<void> fetchHomeData() async {
    _isLoading = true;
    notifyListeners();

    try {
      final results = await Future.wait([
        _apiService.get('/catalog/products/?featured=true'),
        _apiService.get('/catalog/products/?trending=true'),
        _apiService.get('/catalog/categories/'),
        _apiService.get('/cms/sliders/'),
      ]);

      final featuredData = results[0];
      final trendingData = results[1];
      final categoryData = results[2];
      final sliderData = results[3];

      if (featuredData != null) {
        final List items = featuredData['results'] ?? featuredData;
        _featuredProducts = items.map((json) => Product.fromJson(json)).toList();
      }

      if (trendingData != null) {
        final List items = trendingData['results'] ?? trendingData;
        _trendingProducts = items.map((json) => Product.fromJson(json)).toList();
      }

      if (categoryData != null) {
        _categories = categoryData['results'] ?? categoryData;
      }

      if (sliderData != null) {
        _sliders = sliderData['results'] ?? sliderData;
      }

    } catch (e) {
      print('Error fetching home data: $e');
    }

    _isLoading = false;
    notifyListeners();
  }
}
