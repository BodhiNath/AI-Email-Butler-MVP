import 'package:flutter/material.dart';
import 'models/ai_action.dart';
import 'services/api_service.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AI Email Butler MVP',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        useMaterial3: true,
      ),
      home: const EmailDashboard(),
    );
  }
}

class EmailDashboard extends StatefulWidget {
  const EmailDashboard({super.key});

  @override
  State<EmailDashboard> createState() => _EmailDashboardState();
}

class _EmailDashboardState extends State<EmailDashboard> {
  final ApiService _apiService = ApiService();
  AiActionSuggestion? _suggestion;
  bool _isLoading = false;
  String _statusMessage = 'Ready to process email.';

  // Mock Email Data for demonstration
  final EmailContext _mockEmail = EmailContext(
    subject: 'Follow up on the Q3 report',
    body: 'Hi, can you please send over the final Q3 report by end of day today? Thanks!',
    sender: 'boss@company.com',
    userId: 'mock_user_123',
    workflowRules: 'If sender is boss@company.com, draft a polite reply confirming receipt and asking for a 24-hour extension.',
  );

  Future<void> _processEmail() async {
    setState(() {
      _isLoading = true;
      _statusMessage = 'Sending email context to AI backend...';
      _suggestion = null;
    });

    try {
      final suggestion = await _apiService.suggestAction(_mockEmail);
      setState(() {
        _suggestion = suggestion;
        _statusMessage = 'AI Suggestion Received!';
      });
    } catch (e) {
      setState(() {
        _statusMessage = 'Error: ${e.toString()}';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('AI Email Butler MVP'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _processEmail,
            tooltip: 'Process Mock Email',
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: <Widget>[
            Text(
              'Status: $_statusMessage',
              style: TextStyle(
                color: _suggestion != null ? Colors.green : Colors.black,
                fontWeight: FontWeight.bold,
              ),
            ),
            const Divider(),
            const Text(
              'Mock Incoming Email:',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            ListTile(
              title: Text(_mockEmail.subject),
              subtitle: Text('From: ${_mockEmail.sender}'),
              trailing: const Icon(Icons.email),
            ),
            const SizedBox(height: 10),
            Text('Body: ${_mockEmail.body}'),
            const SizedBox(height: 20),
            Center(
              child: _isLoading
                  ? const CircularProgressIndicator()
                  : ElevatedButton.icon(
                      onPressed: _processEmail,
                      icon: const Icon(Icons.auto_awesome),
                      label: const Text('Run AI Workflow'),
                    ),
            ),
            const Divider(height: 30),
            if (_suggestion != null)
              Expanded(
                child: SingleChildScrollView(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'AI Action Suggestion:',
                        style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.blue),
                      ),
                      _buildSuggestionDetail('Action', _suggestion!.action),
                      _buildSuggestionDetail('Confidence', _suggestion!.confidence.toStringAsFixed(2)),
                      _buildSuggestionDetail('Send Permission', _suggestion!.sendPermission),
                      if (_suggestion!.replyText != null)
                        _buildSuggestionDetail('Draft Reply', _suggestion!.replyText!),
                      if (_suggestion!.suggestedWorkflowId != null)
                        _buildSuggestionDetail('Workflow ID', _suggestion!.suggestedWorkflowId!),
                    ],
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildSuggestionDetail(String title, String value) {
    return Padding(
      padding: const EdgeInsets.only(top: 8.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '$title:',
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
          Text(value),
        ],
      ),
    );
  }
}
