import os
from pathlib import Path

# Setup MSYS2 DLL directories for WeasyPrint on Windows
if hasattr(os, "add_dll_directory"):
    os.add_dll_directory(r"C:\msys64\ucrt64\bin")
os.environ["WEASYPRINT_DLL_DIRECTORIES"] = r"C:\msys64\ucrt64\bin"

BASE_DIR = Path(__file__).parent.parent.resolve()

FILES_CONFIG = [
    # Part I: Foundations
    ("0_Foundations/README.md", 1, "Foundations", None, "part_intro"),
    ("0_Foundations/0_System_Evolution.md", 1, "Foundations", 1, "chapter"),
    ("0_Foundations/1_Asynchronous_Processing.md", 1, "Foundations", 2, "chapter"),
    ("0_Foundations/2_Performance_Engineering_Basics.md", 1, "Foundations", 3, "chapter"),
    ("0_Foundations/3_Common_Bottlenecks_and_Testing.md", 1, "Foundations", 4, "chapter"),

    # Part II: Data Storage
    ("1_Data_Storage/README.md", 2, "Data Storage", None, "part_intro"),
    ("1_Data_Storage/1_Relational_Databases/0_Database_Bottlenecks_and_Replication.md", 2, "Data Storage", 1, "chapter"),
    ("1_Data_Storage/1_Relational_Databases/1_Database_Sharding_and_Strategies.md", 2, "Data Storage", 2, "chapter"),
    ("1_Data_Storage/1_Relational_Databases/2_CRUD_Operations_and_Performance.md", 2, "Data Storage", 3, "chapter"),
    ("1_Data_Storage/1_Relational_Databases/3_CRUD_Patterns_at_Scale.md", 2, "Data Storage", 4, "chapter"),
    ("1_Data_Storage/2_In_Memory_Caching/Redis/0_INTRO.md", 2, "Data Storage", 5, "chapter"),
    ("1_Data_Storage/2_In_Memory_Caching/Redis/1_BASICS.md", 2, "Data Storage", 6, "chapter"),
    ("1_Data_Storage/2_In_Memory_Caching/Redis/2_DATA_TYPES.md", 2, "Data Storage", 7, "chapter"),
    ("1_Data_Storage/2_In_Memory_Caching/Redis/3_COMMANDS.md", 2, "Data Storage", 8, "chapter"),
    ("1_Data_Storage/2_In_Memory_Caching/Redis/4_PUBSUB.md", 2, "Data Storage", 9, "chapter"),
    ("1_Data_Storage/2_In_Memory_Caching/Redis/5_SYSTEMS_PERSPECTIVE.md", 2, "Data Storage", 10, "chapter"),
    ("1_Data_Storage/2_In_Memory_Caching/Redis/6_REDIS_DESIGN_AND_MISTAKES.md", 2, "Data Storage", 11, "chapter"),

    # Part III: Async and Events
    ("2_Async_and_Events/README.md", 3, "Async and Events", None, "part_intro"),
    ("2_Async_and_Events/0_Messaging/0_Messaging_Patterns.md", 3, "Async and Events", 1, "chapter"),
    ("2_Async_and_Events/0_Messaging/1_Message_Semantics_and_Mistakes.md", 3, "Async and Events", 2, "chapter"),
    ("2_Async_and_Events/1_Event_Streaming/Kafka/0_INTRO.md", 3, "Async and Events", 3, "chapter"),
    ("2_Async_and_Events/1_Event_Streaming/Kafka/1_BASICS.md", 3, "Async and Events", 4, "chapter"),
    ("2_Async_and_Events/1_Event_Streaming/Kafka/2_CONCEPTS.md", 3, "Async and Events", 5, "chapter"),
    ("2_Async_and_Events/1_Event_Streaming/Kafka/3_INTERNALS.md", 3, "Async and Events", 6, "chapter"),
    ("2_Async_and_Events/1_Event_Streaming/Kafka/4_SYSTEMS_PERSPECTIVE.md", 3, "Async and Events", 7, "chapter"),
    ("2_Async_and_Events/1_Event_Streaming/Kafka/5_KAFKA_DESIGN_AND_MISTAKES.md", 3, "Async and Events", 8, "chapter"),
    ("2_Async_and_Events/2_Distributed_Transactions/0_Distributed_Transactions.md", 3, "Async and Events", 9, "chapter"),
    ("2_Async_and_Events/2_Distributed_Transactions/1_Saga_Pattern_Overview.md", 3, "Async and Events", 10, "chapter"),
    ("2_Async_and_Events/2_Distributed_Transactions/2_Saga_Pattern_Deep_Dive.md", 3, "Async and Events", 11, "chapter"),

    # Part IV: Reliability and Availability
    ("3_Reliability_and_Availability/README.md", 4, "Reliability and Availability", None, "part_intro"),
    ("3_Reliability_and_Availability/0_Reliability_Patterns.md", 4, "Reliability and Availability", 1, "chapter"),
    ("3_Reliability_and_Availability/1_Resource_Isolation_and_Fault_Tolerance.md", 4, "Reliability and Availability", 2, "chapter"),
    ("3_Reliability_and_Availability/2_Availability_and_Replication.md", 4, "Reliability and Availability", 3, "chapter"),
    ("3_Reliability_and_Availability/3_Failover_and_Multi_Region.md", 4, "Reliability and Availability", 4, "chapter"),

    # Part V: Infrastructure
    ("4_Infrastructure/README.md", 5, "Infrastructure", None, "part_intro"),
    ("4_Infrastructure/0_Server_Fundamentals/0_Under_the_Hood.md", 5, "Infrastructure", 1, "chapter"),
    ("4_Infrastructure/0_Server_Fundamentals/1_Web_Server_Overview.md", 5, "Infrastructure", 2, "chapter"),

    # Part VI: API Design
    ("6_API_Design/README.md", 6, "API Design", None, "part_intro"),
    ("6_API_Design/0_API_Communication_Protocols.md", 6, "API Design", 1, "chapter"),
    ("6_API_Design/1_REST_API_Design.md", 6, "API Design", 2, "chapter"),
    ("6_API_Design/2_GraphQL.md", 6, "API Design", 3, "chapter"),
    ("6_API_Design/3_gRPC.md", 6, "API Design", 4, "chapter"),
    ("6_API_Design/4_API_State_Management.md", 6, "API Design", 5, "chapter"),
    ("6_API_Design/5_API_Versioning.md", 6, "API Design", 6, "chapter"),
    ("6_API_Design/6_Authentication_and_Authorization.md", 6, "API Design", 7, "chapter"),
    ("6_API_Design/7_API_Security_and_Rate_Limiting.md", 6, "API Design", 8, "chapter"),
    ("6_API_Design/8_API_Gateway_and_Load_Balancing.md", 6, "API Design", 9, "chapter"),

    # Part VII: Operations
    ("5_Operations/README.md", 7, "Operations", None, "part_intro"),
    ("5_Operations/0_Observability_Fundamentals.md", 7, "Operations", 1, "chapter"),
    ("5_Operations/1_Systematic_Debugging_and_Failure_Patterns.md", 7, "Operations", 2, "chapter"),
]

PART_NUMBERS_ROMAN = {
    1: "I", 2: "II", 3: "III", 4: "IV",
    5: "V", 6: "VI", 7: "VII",
}
