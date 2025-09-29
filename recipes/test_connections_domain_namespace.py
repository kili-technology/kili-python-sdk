#!/usr/bin/env python3
"""Demo script for the ConnectionsNamespace domain API.

This script demonstrates how to use the new Connections domain namespace
to manage cloud storage connections in Kili projects.

Note: This is a demonstration script. In real usage, you would need:
- Valid API credentials
- Existing cloud storage integrations
- Valid project IDs
"""


def demo_connections_namespace():
    """Demonstrate the Connections domain namespace functionality."""
    print("🔗 Kili ConnectionsNamespace Demo")
    print("=" * 50)

    # Initialize Kili client (would need real API key in practice)
    print("\n1. Initializing Kili client...")
    # kili = Kili(api_key="your-api-key-here")

    # For demo purposes, we'll show the API structure
    print("   ✓ Client initialized with connections namespace available")
    print("   Access via: kili.connections or kili.connections (in non-legacy mode)")

    print("\n2. Available Operations:")
    print("   📋 list()  - Query and list cloud storage connections")
    print("   ➕ add()   - Connect cloud storage integration to project")
    print("   🔄 sync()  - Synchronize connection with cloud storage")

    print("\n3. Example Usage Patterns:")

    print("\n   📋 List connections for a project:")
    print("   ```python")
    print("   connections = kili.connections.list(project_id='project_123')")
    print("   print(f'Found {len(connections)} connections')")
    print("   ```")

    print("\n   ➕ Add a new connection with filtering:")
    print("   ```python")
    print("   result = kili.connections.add(")
    print("       project_id='project_123',")
    print("       cloud_storage_integration_id='integration_456',")
    print("       prefix='data/images/',")
    print("       include=['*.jpg', '*.png'],")
    print("       exclude=['**/temp/*']")
    print("   )")
    print("   connection_id = result['id']")
    print("   ```")

    print("\n   🔄 Synchronize connection (with dry-run preview):")
    print("   ```python")
    print("   # Preview changes first")
    print("   preview = kili.connections.sync(")
    print("       connection_id='connection_789',")
    print("       dry_run=True")
    print("   )")
    print("   ")
    print("   # Apply changes")
    print("   result = kili.connections.sync(")
    print("       connection_id='connection_789',")
    print("       delete_extraneous_files=False")
    print("   )")
    print("   print(f'Synchronized {result[\"numberOfAssets\"]} assets')")
    print("   ```")

    print("\n4. Key Features:")
    print("   🎯 Simplified API focused on connections (vs general cloud storage)")
    print("   🛡️  Enhanced error handling with user-friendly messages")
    print("   ✅ Input validation for required parameters")
    print("   📊 Comprehensive type hints and documentation")
    print("   🔄 Lazy loading and memory optimizations via base class")
    print("   🧪 Dry-run support for safe synchronization testing")

    print("\n5. Integration Benefits:")
    print("   • Clean separation: connections vs cloud storage integrations")
    print("   • Consistent API patterns across all domain namespaces")
    print("   • Better discoverability through focused namespace")
    print("   • Enhanced user experience for cloud storage workflows")

    print("\n✨ ConnectionsNamespace Demo Complete!")
    print("=" * 50)


if __name__ == "__main__":
    demo_connections_namespace()
