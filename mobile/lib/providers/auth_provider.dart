import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/api_service.dart';

class AuthProvider with ChangeNotifier {
  final ApiService _apiService = ApiService();
  
  bool _isAuthenticated = false;
  bool _isLoading = true;
  String? _username;

  bool get isAuthenticated => _isAuthenticated;
  bool get isLoading => _isLoading;
  String? get username => _username;

  AuthProvider() {
    checkAuthStatus();
  }

  Future<void> checkAuthStatus() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('access_token');
    
    if (token != null) {
      _isAuthenticated = true;
      // Optionally fetch user profile to verify token validity
      try {
        final userData = await _apiService.get('/users/me/');
        if (userData != null && userData['user'] != null) {
          _username = userData['user']['username'];
        }
      } catch (e) {
        // If token is invalid/expired
        await logout();
      }
    }
    
    _isLoading = false;
    notifyListeners();
  }

  Future<bool> login(String username, String password) async {
    try {
      _isLoading = true;
      notifyListeners();

      final response = await _apiService.post('/auth/login/', {
        'username': username,
        'password': password,
      });

      if (response != null && response['access'] != null) {
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('access_token', response['access']);
        if (response['refresh'] != null) {
          await prefs.setString('refresh_token', response['refresh']);
        }
        
        _isAuthenticated = true;
        _username = response['user']?['username'] ?? username;
        _isLoading = false;
        notifyListeners();
        return true;
      }
      
      _isLoading = false;
      notifyListeners();
      return false;
    } catch (e) {
      _isLoading = false;
      notifyListeners();
      throw e;
    }
  }

  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('access_token');
    await prefs.remove('refresh_token');
    
    _isAuthenticated = false;
    _username = null;
    notifyListeners();
  }
}
