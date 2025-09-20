# GraphQL CRM System

A Django-based Customer Relationship Management (CRM) system with GraphQL API integration.

## Features

- **GraphQL API**: Single endpoint for all data operations
- **Customer Management**: Create, read, update customers with validation
- **Product Management**: Manage products with pricing and inventory
- **Order Management**: Create orders with multiple products
- **Advanced Filtering**: Filter customers, products, and orders with various criteria
- **Bulk Operations**: Bulk customer creation with partial success handling
- **Data Validation**: Comprehensive validation for all inputs

## Setup Instructions

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Seed Database (Optional)**
   ```bash
   python seed_db.py
   ```

4. **Start Development Server**
   ```bash
   python manage.py runserver
   ```

5. **Access GraphQL Interface**
   - Open your browser and go to: `http://localhost:8000/graphql`
   - Use the GraphiQL interface to test queries and mutations

## GraphQL Schema

### Queries

- `hello`: Returns a greeting message
- `allCustomers`: Get all customers with filtering options
- `allProducts`: Get all products with filtering options
- `allOrders`: Get all orders with filtering options

### Mutations

- `createCustomer`: Create a single customer
- `bulkCreateCustomers`: Create multiple customers at once
- `createProduct`: Create a new product
- `createOrder`: Create an order with products

### Example Queries

#### Create a Customer
```graphql
mutation {
  createCustomer(input: {
    name: "John Doe"
    email: "john@example.com"
    phone: "+1234567890"
  }) {
    customer {
      id
      name
      email
      phone
    }
    message
  }
}
```

#### Filter Customers
```graphql
query {
  allCustomers(filter: { nameIcontains: "John" }) {
    edges {
      node {
        id
        name
        email
        createdAt
      }
    }
  }
}
```

#### Create an Order
```graphql
mutation {
  createOrder(input: {
    customerId: "1"
    productIds: ["1", "2"]
  }) {
    order {
      id
      customer {
        name
      }
      products {
        name
        price
      }
      totalAmount
      orderDate
    }
  }
}
```

## Project Structure

```
alx-backend-graphql_crm/
├── alx_backend_graphql_crm/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── asgi.py
│   └── schema.py
├── crm/
│   ├── __init__.py
│   ├── models.py
│   ├── schema.py
│   ├── filters.py
│   ├── admin.py
│   ├── apps.py
│   ├── views.py
│   ├── urls.py
│   └── tests.py
├── manage.py
├── requirements.txt
├── seed_db.py
└── README.md
```

## Technologies Used

- **Django**: Web framework
- **GraphQL**: Query language and runtime
- **Graphene-Django**: GraphQL integration for Django
- **Django-Filter**: Advanced filtering capabilities
- **SQLite**: Database (default)

## Validation Rules

- **Email**: Must be unique across customers
- **Phone**: Must match format like `+1234567890` or `123-456-7890`
- **Price**: Must be positive
- **Stock**: Must be non-negative
- **Orders**: Must have at least one product and valid customer
