@echo off
echo Testing Sales Analytics Chat Assistant API
echo ===========================================
echo.

REM Test 1: Health check
echo Test 1: Health Check
curl -s http://localhost:8000/health
echo.
echo.

REM Test 2: Sales query - Total sales this month
echo Test 2: Sales Query - "What were total sales this month?"
curl -s -X POST http://localhost:8000/api/query/sales -H "Content-Type: application/json" -d "{\"query\": \"What were total sales this month?\", \"user_id\": \"test_user\"}"
echo.
echo.

REM Test 3: Sales query - Top products
echo Test 3: Sales Query - "Show me top selling products"
curl -s -X POST http://localhost:8000/api/query/sales -H "Content-Type: application/json" -d "{\"query\": \"Show me top selling products\", \"user_id\": \"test_user\"}"
echo.
echo.

REM Test 4: Sales query - Last week
echo Test 4: Sales Query - "Sales from last week"
curl -s -X POST http://localhost:8000/api/query/sales -H "Content-Type: application/json" -d "{\"query\": \"Sales from last week\", \"user_id\": \"test_user\"}"
echo.
echo.

echo ===========================================
echo All tests completed!
pause
