# گزارش تحویل و ادامه پروژه AutoParts Sales Intelligence

این فایل وضعیت کامل پروژه تا پایان مرحله انتقال داده‌های خام به Microsoft SQL Server را ثبت می‌کند. اگر Work فعلی از دسترس خارج شد، این فایل را به Work جدید بده و تأکید کن که مراحل انجام‌شده تکرار نشوند و کار دقیقاً از بخش «نقطه ادامه پروژه» دنبال شود.

## قواعد ادامه کار

- دیتابیس انتخاب‌شده Microsoft SQL Server است، نه PostgreSQL.
- سیستم‌عامل پروژه Windows 10 Pro است.
- کاربر در SQL و Power BI تازه‌کار است؛ هر بار فقط یک مرحله یا یک دستور ارائه شود و سپس منتظر خروجی کاربر بمانید.
- مسیرها و نام فایل‌های موجود تغییر نکنند، مگر اینکه دلیل فنی مشخصی وجود داشته باشد.
- پیش از هر Commit، وضعیت Git و فایل‌های تغییرکرده بررسی شوند.
- هدف نهایی پروژه، ساخت یک نمونه‌کار حرفه‌ای برای تحلیل فروش عمده قطعات خودرو با Python، SQL Server، Power BI، n8n و یک AI Agent است.

## مشخصات پروژه

نام پروژه:

```text
autoparts-sales-intelligence
```

مسیر محلی:

```text
D:\AI-Projects\autoparts-sales-intelligence
```

مخزن GitHub:

```text
https://github.com/kimdijavad-spec/autoparts-sales-intelligence
```

شاخه اصلی:

```text
main
```

وضعیت فعلی Git:

- شاخه محلی با `origin/main` هماهنگ است.
- خروجی `git status --short` خالی است.
- Working Tree تمیز است.
- آخرین Commit فعلی:

```text
4fa1e40 feat: load validated CSV data into SQL Server
```

Commitهای مهم اخیر:

```text
4fa1e40 feat: load validated CSV data into SQL Server
0d49e3c feat: add SQL Server database schema
d57f571 feat: integrate data validation into generation pipeline
a129381 feat: add comprehensive data quality validation
1d0f493 feat: add end-to-end data generation pipeline
8f2bca4 chore: define repository line ending rules
```

## محیط Python

محیط مجازی پروژه فعال است:

```text
D:\AI-Projects\autoparts-sales-intelligence\.venv
```

فایل وابستگی‌ها:

```text
requirements.txt
```

وابستگی‌های ثبت‌شده:

```text
et_xmlfile==2.0.0
Faker==40.37.0
numpy==2.5.2
openpyxl==3.1.5
pandas==3.0.5
python-dateutil==2.9.0.post0
six==1.17.0
tzdata==2026.3
pyodbc==5.3.0
```

نسخه نصب‌شده `pyodbc`:

```text
5.3.0
```

## تولید و اعتبارسنجی داده‌ها

اسکریپت اجرای کامل خط تولید داده:

```text
src/generate_all_data.py
```

دستور اجرا:

```powershell
python src/generate_all_data.py
```

این Pipeline هفت مرحله تولید داده را اجرا می‌کند و در مرحله هشتم، اعتبارسنجی جامع را با فایل زیر انجام می‌دهد:

```text
src/validate_all_data.py
```

اگر یکی از مراحل تولید یا اعتبارسنجی شکست بخورد، Pipeline با کد خطا متوقف می‌شود و پیام موفقیت نمایش داده نمی‌شود.

آخرین اجرای کامل Pipeline موفق بوده و نتیجه اعتبارسنجی:

```text
RESULT: PASSED
All schema, completeness, relationship, and business-rule checks passed.
```

## فایل‌های داده خام

مسیر فایل‌ها:

```text
D:\AI-Projects\autoparts-sales-intelligence\data\raw
```

فایل‌ها و تعداد رکوردها:

| فایل | تعداد رکورد |
| --- | ---: |
| `sales_representatives.csv` | 12 |
| `customers.csv` | 500 |
| `products.csv` | 300 |
| `campaigns.csv` | 12 |
| `campaign_targets.csv` | 1,626 |
| `sales_orders.csv` | 8,000 |
| `sales_order_lines.csv` | 25,000 |
| `payments.csv` | 8,000 |
| مجموع | 43,450 |

ویژگی‌های مهم داده‌ها:

- تاریخ‌ها با قالب `YYYY-MM-DD` ذخیره شده‌اند.
- مقادیر منطقی CSV به شکل `True` و `False` هستند.
- بعضی مقادیر `campaign_id` در `sales_orders.csv` خالی هستند و هنگام بارگذاری به `NULL` تبدیل می‌شوند.
- بعضی مقادیر `paid_date` در `payments.csv` خالی هستند و هنگام بارگذاری به `NULL` تبدیل می‌شوند.
- مبالغ عدد صحیح و بدون اعشار هستند.
- همه فایل‌ها پیش از ورود به SQL Server از اعتبارسنجی جامع عبور کرده‌اند.

ستون‌های فایل‌ها:

```text
sales_representatives.csv:
sales_rep_id, sales_rep_name, region, hire_date, monthly_target, status

customers.csv:
customer_id, customer_name, customer_type, province, city,
registration_date, credit_limit, sales_rep_id, status

products.csv:
product_id, sku, product_name, category, brand, compatible_vehicle,
unit_cost, list_price, reorder_point, status

campaigns.csv:
campaign_id, campaign_name, channel, start_date, end_date, budget,
target_customer_type, target_product_category, offered_discount

campaign_targets.csv:
campaign_id, customer_id, contact_date, message_delivered,
customer_engaged, sales_followup, converted

sales_orders.csv:
order_id, order_date, customer_id, sales_rep_id, campaign_id,
payment_method

sales_order_lines.csv:
order_line_id, order_id, product_id, quantity, unit_price,
discount_percent, returned_quantity

payments.csv:
payment_id, order_id, customer_id, invoice_amount, invoice_date,
due_date, paid_date, payment_status
```

## نصب Microsoft SQL Server

نسخه نصب‌شده:

```text
Microsoft SQL Server 2025 Standard Developer Edition
```

نسخه موتور دیتابیس:

```text
Microsoft SQL Server 2025 (RTM)
17.0.1000.7
```

تنظیمات نصب:

- نوع نصب: نصب جدید SQL Server.
- قابلیت نصب‌شده: `Database Engine Services`.
- Azure Extension غیرفعال شد.
- نوع نمونه: Default instance.
- نام نمونه: `MSSQLSERVER`.
- سرویس Database Engine روی حالت Automatic است.
- سرویس SQL Server Agent روی حالت Manual است.
- سرویس SQL Server Browser غیرفعال است.
- گزینه Grant Perform Volume Maintenance Tasks privilege فعال شد.
- روش احراز هویت Windows Authentication است.
- حساب فعلی ویندوز با Add Current User به مدیران SQL Server اضافه شد.
- نصب با وضعیت Succeeded کامل شد.

## نصب SQL Server Management Studio

نسخه نصب‌شده:

```text
SQL Server Management Studio 22
Version 22.9.2
```

مسیر فایل اجرایی:

```text
C:\Program Files\Microsoft SQL Server Management Studio 22\Release\Common7\IDE\SSMS.exe
```

دستور اجرای SSMS در PowerShell:

```powershell
& "C:\Program Files\Microsoft SQL Server Management Studio 22\Release\Common7\IDE\SSMS.exe"
```

ورود به حساب Microsoft یا GitHub انجام نشده و گزینه زیر انتخاب شده است:

```text
Skip and add accounts later
```

قابلیت‌های اختیاری AI Assistance، Business Intelligence، Hybrid and Migration، Code tools و Database DevOps نصب نشده‌اند.

Power BI Report Server عمداً نصب نشده است. Power BI Desktop نیز هنوز نصب نشده و قرار است در مرحله ساخت داشبورد نصب شود.

## تنظیمات اتصال SQL Server

تنظیمات اتصال موفق در SSMS:

```text
Server Name: localhost
Authentication: Windows Authentication
Encrypt: Mandatory
Trust Server Certificate: Enabled
Database Name: <default>
```

درایورهای ODBC نصب‌شده شامل نسخه‌های ۱۷ و ۱۸ هستند. پروژه از درایور ۶۴ بیتی زیر استفاده می‌کند:

```text
ODBC Driver 18 for SQL Server
```

اتصال Python با `pyodbc` آزمایش شده و نام دیتابیس زیر با موفقیت بازگردانده شده است:

```text
autoparts_sales_intelligence
```

## دیتابیس و ساختار SQL

نام دیتابیس:

```text
autoparts_sales_intelligence
```

Schemaهای منطقی:

```text
sales
inventory
marketing
finance
```

جدول‌ها:

```text
sales.sales_representatives
sales.customers
inventory.products
marketing.campaigns
marketing.campaign_targets
sales.sales_orders
sales.sales_order_lines
finance.payments
```

روابط اصلی:

- هر مشتری به یک نماینده فروش متصل است.
- اهداف کمپین به کمپین و مشتری متصل‌اند.
- هر سفارش به مشتری و نماینده فروش متصل است و ممکن است به یک کمپین متصل باشد.
- اقلام سفارش به سفارش و محصول متصل‌اند.
- پرداخت از طریق ترکیب `order_id + customer_id` به همان سفارش و همان مشتری متصل است.

## فایل‌های SQL

### ساخت دیتابیس

```text
sql/01_create_database.sql
```

این فایل فقط در صورت نبود دیتابیس، آن را ایجاد می‌کند و قابل اجرای مجدد است.

### ساخت Schemaها و جدول‌ها

```text
sql/02_create_schema.sql
```

این فایل ۴ Schema و ۸ جدول را همراه با کلیدهای اصلی، کلیدهای خارجی، قیدهای یکتا، مقادیر پیش‌فرض و محدودیت‌های کسب‌وکار می‌سازد. ساخت اشیا به‌صورت قابل‌تکرار نوشته شده است.

### افزایش اندازه وضعیت محصول

```text
sql/03_expand_product_status.sql
```

در ساختار اولیه، ستون زیر `NVARCHAR(20)` بود:

```text
inventory.products.status
```

مقدار `Temporarily Unavailable` دارای ۲۳ کاراکتر بود و در ستون جا نمی‌شد. فایل مرحله سوم اندازه ستون را به شکل قابل‌تکرار به مقدار زیر افزایش می‌دهد:

```text
NVARCHAR(30)
```

این فایل در SSMS اجرا شده و پیام `Commands completed successfully` دریافت شده است.

## اسکریپت بارگذاری SQL Server

مسیر فایل:

```text
src/load_data_to_sql_server.py
```

دستور اجرا:

```powershell
python src/load_data_to_sql_server.py
```

وظایف اسکریپت:

- پیدا کردن فایل‌ها نسبت به ریشه پروژه.
- بررسی نام و ترتیب ستون‌های CSV پیش از تغییر دیتابیس.
- تبدیل تاریخ‌ها به نوع تاریخ Python و سپس SQL Server.
- تبدیل مقدارهای `True` و `False` به `BIT`.
- تبدیل `campaign_id` و `paid_date` خالی به `NULL`.
- تبدیل مقادیر عددی به انواع مناسب.
- اتصال با Windows Authentication و ODBC Driver 18.
- پاک‌سازی داده‌های قبلی در ترتیب معکوس وابستگی‌ها.
- ورود داده‌ها در ترتیب صحیح کلیدهای خارجی.
- انجام کل عملیات در یک تراکنش.
- بازگردانی کامل تراکنش در صورت هر خطا.
- مقایسه تعداد ردیف هر جدول SQL با فایل CSV متناظر پیش از Commit تراکنش.

ترتیب ورود جدول‌ها:

```text
1. sales.sales_representatives
2. sales.customers
3. inventory.products
4. marketing.campaigns
5. marketing.campaign_targets
6. sales.sales_orders
7. sales.sales_order_lines
8. finance.payments
```

ترتیب پاک‌سازی معکوس همین وابستگی‌هاست.

### خطای حل‌شده pyodbc

در اجرای اول، گزینه `fast_executemany` باعث خطای بافر رشته شد:

```text
String data, right truncation: length 46 buffer 40
```

این گزینه در نسخه فعلی اسکریپت غیرفعال شده است تا طول رشته‌ها براساس ردیف‌های ابتدایی محدود نشود.

در اجرای بعدی، خطای واقعی کوچک‌بودن ستون `inventory.products.status` شناسایی شد. فایل `03_expand_product_status.sql` این مشکل را رفع کرد.

## نتیجه نهایی بارگذاری

آخرین اجرای `src/load_data_to_sql_server.py` با موفقیت کامل شد:

```text
DATA LOAD COMPLETED SUCCESSFULLY
All CSV and SQL Server row counts match.
```

نتیجه تطبیق تعداد رکوردها:

| جدول | CSV | SQL Server | نتیجه |
| --- | ---: | ---: | --- |
| `sales.sales_representatives` | 12 | 12 | PASS |
| `sales.customers` | 500 | 500 | PASS |
| `inventory.products` | 300 | 300 | PASS |
| `marketing.campaigns` | 12 | 12 | PASS |
| `marketing.campaign_targets` | 1,626 | 1,626 | PASS |
| `sales.sales_orders` | 8,000 | 8,000 | PASS |
| `sales.sales_order_lines` | 25,000 | 25,000 | PASS |
| `finance.payments` | 8,000 | 8,000 | PASS |

در حال حاضر هر ۸ جدول پر هستند و مجموعاً ۴۳٬۴۵۰ رکورد در SQL Server قرار دارد.

## وضعیت فعلی فایل‌ها و Git

فایل‌های زیر در Commit شماره `4fa1e40` ثبت و به GitHub ارسال شده‌اند:

```text
requirements.txt
sql/03_expand_product_status.sql
src/load_data_to_sql_server.py
```

بعد از Push، دستور زیر هیچ خروجی نداشت:

```powershell
git status --short
```

بنابراین مخزن در نقطه فعلی تمیز و با GitHub هماهنگ است.

## نقطه ادامه پروژه

تمام مراحل زیر کامل شده‌اند و نباید تکرار شوند:

- تولید داده‌های مصنوعی.
- اعتبارسنجی جامع داده‌های خام.
- اتصال اعتبارسنجی به Pipeline تولید داده.
- نصب و تنظیم SQL Server 2025.
- نصب و تنظیم SSMS 22.
- ساخت دیتابیس.
- ساخت Schemaها و جدول‌های عملیاتی.
- نصب و ثبت `pyodbc`.
- ساخت اسکریپت ورود داده.
- انتقال هر ۸ CSV به SQL Server.
- تطبیق کامل تعداد رکوردهای CSV و SQL Server.
- ثبت و ارسال تمام تغییرات تا Commit شماره `4fa1e40`.

مرحله بعدی پروژه:

```text
طراحی و ساخت لایه تحلیلی SQL برای تحلیل فروش، مشتریان، محصولات، کمپین‌ها، نمایندگان فروش، مرجوعی‌ها و وضعیت وصول مطالبات
```

پیش از ساخت فایل SQL جدید، باید درباره مدل تحلیلی موردنیاز تصمیم گرفته شود. سپس Queryها یا Viewهای تحلیلی به‌صورت مرحله‌بندی‌شده داخل پوشه `sql` ساخته، در SSMS اجرا، با داده واقعی آزمایش و پس از تأیید Commit شوند.

Power BI Desktop هنوز نصب نشده است. نصب آن باید بعد از آماده‌شدن لایه تحلیلی SQL و هنگام شروع ساخت داشبورد انجام شود.

## پیام پیشنهادی برای Work جدید

در صورت نیاز، همراه با ارسال این فایل، پیام زیر را نیز بفرست:

```text
این فایل گزارش کامل پروژه autoparts-sales-intelligence تا آخرین وضعیت فعلی است. لطفاً آن را کامل بخوان، هیچ‌کدام از مراحل انجام‌شده را تکرار نکن و دقیقاً از بخش «نقطه ادامه پروژه» کار را دنبال کن. من در SQL و Power BI تازه‌کار هستم؛ بنابراین هر بار فقط یک مرحله یا یک دستور بده و منتظر خروجی من بمان.
```
