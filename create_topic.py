from confluent_kafka.admin import AdminClient, NewTopic

# Define Kafka admin client
admin_client = AdminClient({"bootstrap.servers": "localhost:9092"})

# Create the topic
topic_name = "weather_data_demo"
new_topic = NewTopic(topic_name, num_partitions=3, replication_factor=1)

# Send request to create topic
future = admin_client.create_topics([new_topic])

# Check if the topic was created successfully
for topic, f in future.items():
    try:
        f.result()  # Wait for result
        print(f"Topic '{topic}' created successfully")
    except Exception as e:
        print(f"Failed to create topic '{topic}': {e}")
