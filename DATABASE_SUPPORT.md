# hMailServer Autonomous Edition - Multi-Database Support

## Supported Database Engines

hMailServer Autonomous Edition supports four major database engines, providing flexibility for different deployment scenarios and enterprise requirements.

### 🔵 Microsoft SQL Server (Recommended)
**Best for: Enterprise Windows environments, Azure integration**

#### Features:
- **Always Encrypted** - Column-level encryption for sensitive data
- **Temporal Tables** - Built-in data versioning and audit trails
- **JSON Support** - Native JSON data type and operations
- **In-Memory OLTP** - Memory-optimized tables for high performance
- **AI Integration** - Azure Cognitive Services integration
- **Advanced Security** - Row-level security and data masking

#### Configuration:
```powershell
# Connection String
"Server=localhost;Database=hMailServerAutonomous;Integrated Security=true;TrustServerCertificate=true"

# Entity Framework Provider
"Microsoft.EntityFrameworkCore.SqlServer"

# Default Port: 1433
# Service Dependency: MSSQLSERVER
```

#### Installation Requirements:
- SQL Server 2019 or later (Express, Standard, or Enterprise)
- SQL Server Management Studio (SSMS) recommended
- Windows Authentication or SQL Authentication
- .NET SqlClient provider

---

### 🟢 MySQL Database
**Best for: Cross-platform environments, web applications**

#### Features:
- **JSON Support** - Native JSON data type with indexing
- **Full-Text Search** - Advanced text search capabilities
- **GIS Support** - Spatial data types and functions
- **Partitioning** - Table partitioning for large datasets
- **InnoDB Cluster** - High availability and auto-failover
- **Performance Schema** - Built-in performance monitoring

#### Configuration:
```powershell
# Connection String
"Server=localhost;Database=hMailServerAutonomous;Uid=hmailserver;Pwd=SecurePassword123!;CharSet=utf8mb4;SslMode=Required"

# Entity Framework Provider
"Pomelo.EntityFrameworkCore.MySql"

# Default Port: 3306
# Service Dependency: MySQL80
```

#### Installation Requirements:
- MySQL 8.0 or later
- MySQL Workbench recommended for administration
- Create dedicated user account for hMailServer
- Enable SSL/TLS encryption
- Configure utf8mb4 character set

---

### 🔴 MariaDB Server
**Best for: Performance-focused deployments, clustering**

#### Features:
- **Aria Storage Engine** - Crash-safe MyISAM replacement
- **ColumnStore** - Columnar storage for analytics
- **Galera Cluster** - Synchronous multi-master replication
- **ThreadPool** - Improved connection handling
- **MaxScale Integration** - Database proxy and load balancer
- **Spider Storage Engine** - Horizontal partitioning

#### Configuration:
```powershell
# Connection String
"Server=localhost;Database=hMailServerAutonomous;Uid=hmailserver;Pwd=SecurePassword123!;CharSet=utf8mb4;SslMode=Required"

# Entity Framework Provider
"Pomelo.EntityFrameworkCore.MySql"

# Default Port: 3306
# Service Dependency: mariadb
```

#### Installation Requirements:
- MariaDB 10.6 or later
- HeidiSQL or phpMyAdmin for administration
- Configure dedicated user with appropriate privileges
- Enable SSL/TLS encryption
- Set up binary logging for replication

---

### 🟡 PostgreSQL Database
**Best for: Advanced SQL features, data integrity**

#### Features:
- **JSONB Support** - Binary JSON with indexing and queries
- **Full-Text Search** - Advanced text search with ranking
- **PostGIS** - Geographic objects and spatial queries
- **Advanced Indexing** - Partial, expression, and multi-column indexes
- **Parallel Queries** - Automatic query parallelization
- **Logical Replication** - Fine-grained replication control

#### Configuration:
```powershell
# Connection String
"Host=localhost;Database=hMailServerAutonomous;Username=hmailserver;Password=SecurePassword123!;SslMode=Require;Include Error Detail=true"

# Entity Framework Provider
"Npgsql.EntityFrameworkCore.PostgreSQL"

# Default Port: 5432
# Service Dependency: postgresql-x64-14
```

#### Installation Requirements:
- PostgreSQL 14 or later
- pgAdmin 4 recommended for administration
- Create dedicated role with appropriate permissions
- Configure SSL/TLS encryption
- Set up connection pooling with PgBouncer

---

## Database Selection During Installation

### Installation Wizard Options

The hMailServer installer provides a database selection dialog with the following options:

1. **Express Installation (SQL Server)**
   - Automatically installs SQL Server Express
   - Creates database and user accounts
   - Optimizes settings for single-server deployment

2. **Custom Database Selection**
   - Choose from supported database engines
   - Specify connection parameters
   - Test connection before proceeding
   - Option to create database automatically

3. **Existing Database**
   - Connect to existing database instance
   - Validate permissions and compatibility
   - Run migration scripts automatically

### Configuration File

Database settings are stored in `appsettings.json`:

```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Server=localhost;Database=hMailServerAutonomous;Integrated Security=true"
  },
  "DatabaseProvider": "SqlServer",
  "DatabaseFeatures": {
    "EnableEncryption": true,
    "EnableAuditing": true,
    "EnableBackup": true,
    "ConnectionPooling": true
  }
}
```

---

## Database Migration and Compatibility

### Entity Framework Migrations

hMailServer uses Entity Framework Core migrations for database schema management:

```powershell
# Generate migration for all database providers
dotnet ef migrations add InitialCreate --context SqlServerDbContext
dotnet ef migrations add InitialCreate --context MySqlDbContext  
dotnet ef migrations add InitialCreate --context PostgreSqlDbContext

# Apply migrations
dotnet ef database update --context SqlServerDbContext
```

### Cross-Database Compatibility

The application uses a database-agnostic data access layer:

- **Abstract Repository Pattern** - Database-independent data operations
- **Provider-Specific Optimizations** - Engine-specific performance tuning
- **Feature Detection** - Automatic adaptation to database capabilities
- **Unified Configuration** - Single configuration interface for all engines

---

## Performance Considerations

### SQL Server
- **Memory Optimization**: Configure buffer pool and memory-optimized tables
- **Indexing Strategy**: Implement columnstore indexes for analytics
- **Partitioning**: Use table partitioning for large email archives
- **Backup Strategy**: Implement differential and log backups

### MySQL/MariaDB
- **InnoDB Configuration**: Optimize buffer pool and log file sizes
- **Query Cache**: Enable and tune query cache for repeated queries
- **Replication**: Set up master-slave replication for read scaling
- **Partitioning**: Implement range or hash partitioning

### PostgreSQL
- **Shared Buffers**: Configure 25% of system memory
- **Connection Pooling**: Use PgBouncer for connection management
- **Vacuum Strategy**: Configure autovacuum for optimal performance
- **Parallel Queries**: Enable parallel query execution

---

## Security Configuration

### Authentication Methods

**SQL Server:**
- Windows Authentication (recommended)
- SQL Server Authentication with strong passwords
- Azure Active Directory integration

**MySQL/MariaDB:**
- Native password authentication
- SHA-256 authentication plugin
- LDAP integration available

**PostgreSQL:**
- MD5 or SCRAM-SHA-256 authentication
- Certificate-based authentication
- LDAP/Active Directory integration

### Encryption

All database connections support:
- **TLS/SSL Encryption** - Encrypted client-server communication
- **At-Rest Encryption** - Database file encryption
- **Column-Level Encryption** - Sensitive data protection
- **Certificate Management** - Automated certificate renewal

---

## Monitoring and Maintenance

### Performance Monitoring

**Built-in Monitoring:**
- Entity Framework Core logging
- Database connection health checks
- Query execution statistics
- Performance counter integration

**Database-Specific Tools:**
- **SQL Server**: SQL Server Management Studio, Azure Data Studio
- **MySQL**: MySQL Workbench, Percona Monitoring
- **MariaDB**: MaxScale Monitor, MariaDB Enterprise Monitor
- **PostgreSQL**: pgAdmin, pg_stat_statements

### Backup Strategies

**Automated Backups:**
- Daily full backups
- Hourly transaction log backups
- Weekly maintenance operations
- Cloud backup integration (Azure, AWS, GCP)

**Recovery Options:**
- Point-in-time recovery
- Geo-redundant backups
- Cross-region replication
- Disaster recovery automation

---

## Migration Between Database Engines

### Database Migration Utility

hMailServer includes a migration utility for switching between database engines:

```powershell
# Export data from current database
.\hMailServerMigration.exe export --source SqlServer --target MySQL

# Import data to new database
.\hMailServerMigration.exe import --source export.json --target PostgreSQL
```

### Migration Process

1. **Schema Export** - Export database schema and constraints
2. **Data Export** - Export all email data and configurations
3. **Target Preparation** - Create and configure target database
4. **Data Import** - Import data with integrity validation
5. **Index Recreation** - Rebuild indexes and optimize performance
6. **Validation** - Verify data integrity and functionality

---

*Last Updated: August 19, 2025*  
*Supported Engines: SQL Server 2019+, MySQL 8.0+, MariaDB 10.6+, PostgreSQL 14+*  
*Entity Framework Core: 8.0 with provider-specific optimizations*