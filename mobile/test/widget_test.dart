import 'package:flutter_test/flutter_test.dart';
import 'package:kaizen/app.dart';

void main() {
  testWidgets('Kaizen home loads from Stitch shell', (tester) async {
    await tester.pumpWidget(const KaizenApp());
    await tester.pumpAndSettle();
    expect(find.text('Kaizen'), findsWidgets);
    expect(find.text('Good evening, Cradle'), findsOneWidget);
    expect(find.text('Practice'), findsOneWidget);
  });
}
