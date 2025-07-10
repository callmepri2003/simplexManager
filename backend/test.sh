
python manage.py migrate --settings=backend.settings.cicd &
SERVER_PID=$!

# Start server in background
python manage.py runserver --settings=backend.settings.cicd &
SERVER_PID=$!

# Start webhook forwarding
stripe listen --forward-to localhost:8000/webhooks/stripe/ &
STRIPE_PID=$!

# Wait for services to start
sleep 3

# Run tests
python manage.py test --settings=backend.settings.cicd

# Cleanup
kill $SERVER_PID $STRIPE_PID