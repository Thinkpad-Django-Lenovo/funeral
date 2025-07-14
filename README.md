# ⚰️ Maliro Community Funeral Reporting System

A modern and lightweight web application built with **Streamlit** and **Supabase (PostgreSQL)** or **MySQL**, designed to track and manage funeral records in a community.

---

## 🌍 Overview

This system enables **reporters** in local communities to log funeral events, and allows **admins** to manage users, view statistics, and export records. It simplifies the way data is collected and used for community-level tracking, planning, and reporting.

---

## ✅ Features

### 👤 User Management
- Register users with name, role, DOB, gender, and village
- Roles: `admin`, `reporter`
- Secure login with hashed passwords
- Role-based dashboards and access control

### 📋 Funeral Reporting (Reporter Role)
- Add funeral details (name, age, gender, date of { birth, death & brial }, cause, village)
- View and search funerals they've added
- Export reports in CSV, Excel, PDF
- Gender-based chart analytics

### 🛠 Admin Dashboard
- Add new users
- View all funerals reported by all users
- Search and filter by name or village
- Gender analysis via bar/pie charts
- Export full funeral records and charts

---

## 🗄️ Database Structure

### `users` Table
| Column         | Type        | Description                  |
|----------------|-------------|------------------------------|
| id             | UUID        | Primary Key                  |
| full_name      | TEXT        | Full legal name              |
| username       | TEXT        | Unique login username        |
| password_hash  | TEXT        | Bcrypt-hashed password       |
| role           | TEXT        | `admin` or `reporter`        |
| village        | TEXT        | User's home village          |
| date_of_birth  | DATE        | DOB                          |
| gender         | TEXT        | `Male` or `Female`           |
| created_at     | TIMESTAMP   | Record creation time         |
| is_active      | BOOLEAN     | Account status               |

### `funerals` Table
| Column         | Type        | Description                  |
|----------------|-------------|------------------------------|
| id             | UUID        | Primary Key                  |
| full_name      | TEXT        | Deceased's name              |
| age            | INT         | Age of the deceased          |
| gender         | TEXT/ENUM   | Gender                       |
| village        | TEXT        | Village                      |
| date_of_birth  | DATE        | Date of Birth                |
| date_of_death  | DATE        | Date of death                |
| date_of_burial | DATE        | Date of burial               |
| cause_of_death | TEXT        | Reason                       |
| reported_by    | UUID        | FK to users table            |
| created_at     | TIMESTAMP   | Record creation time         |

---

## 🚀 Installation

1. **Clone the repo**
```bash
git clone https://github.com/Thinkpad-Django-Lenovo/funeral.git
cd funeral
"# funeral" 
