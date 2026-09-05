# گزارش تحویل و ادامه پروژه AutoParts Sales Intelligence

این فایل وضعیت کامل پروژه را تا پایان ساخت و اعتبارسنجی لایه تحلیلی Microsoft SQL Server ثبت می‌کند. اگر Work فعلی از دسترس خارج شد، این فایل را به Work جدید بده و تأکید کن مراحل کامل‌شده تکرار نشوند و کار دقیقاً از بخش «نقطه ادامه پروژه» دنبال شود.

## قواعد ادامه کار

- دیتابیس انتخاب‌شده **Microsoft SQL Server** است، نه PostgreSQL.
- سیستم‌عامل پروژه Windows 10 Pro است.
- کاربر در SQL و Power BI تازه‌کار است؛ هر بار فقط یک مرحله یا یک دستور ارائه شود و سپس منتظر خروجی کاربر بمانید.
- توضیحات به فارسی نوشته شوند و فقط نام ابزارها، کدها، Queryها و خروجی‌های فنی انگلیسی باقی بمانند.
- مسیرها و نام فایل‌های موجود تغییر نکنند، مگر اینکه دلیل فنی مشخصی وجود داشته باشد.
- هنگام تحویل فایل دانلودی، دستور بررسی کامل‌بودن همان فایل نیز در همان پاسخ ارائه شود.
- پیش از هر Commit، `git status --short` و سپس `git diff --cached --check` بررسی شوند.
- هدف نهایی، ساخت نمونه‌کار حرفه‌ای تحلیل فروش عمده قطعات خودرو با Python، SQL Server، Power BI، n8n و یک AI Agent است.

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
- Working Tree تمیز است.
- آخرین Commit روی سیستم و GitHub:

```text
ee3a5e0 feat: add validated SQL analytics layer
```

Commitهای مهم اخیر:

```text
ee3a5e0 feat: add validated SQL analytics layer
32e6437 docs: add project handoff report
4fa1e40 feat: load validated CSV data into SQL Server
0d49e3c feat: add SQL Server database schema
d57f571 feat: integrate data validation into generation pipeline
a129381 feat: add comprehensive data quality validation
1d0f493 feat: add end-to-end data generation pipeline
8f2bca4 chore: define repository line ending rules
```

## محیط Python

محیط مجازی پروژه:

```text
D:\AI-Projects\autoparts-sales-intelligence\.venv
```

Python فعال پروژه:

```text
D:\AI-Projects\autoparts-sales-intelligence\.venv\Scripts\python.exe
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

## تولید و اعتبارسنجی داده‌های خام

اسکریپت اجرای کامل Pipeline:

```text
src/generate_all_data.py
```

دستور اجرا:

```powershell
python src/generate_all_data.py
```

Pipeline هفت مرحله تولید داده را اجرا می‌کند و در مرحله هشتم فایل زیر را برای اعتبارسنجی جامع فراخوانی می‌کند:

```text
src/validate_all_data.py
```

آخرین اجرای کامل Pipeline موفق بوده است:

```text
PIPELINE COMPLETED SUCCESSFULLY
RESULT: PASSED
All schema, completeness, relationship, and business-rule checks passed.
```

## فایل‌های داده خام

مسیر:

```text
D:\AI-Projects\autoparts-sales-intelligence\data\raw
```

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
| **مجموع** | **43,450** |

ویژگی‌های مهم:

- تاریخ‌ها با قالب `YYYY-MM-DD` ذخیره شده‌اند.
- مقادیر منطقی CSV به شکل `True` و `False` هستند.
- `campaign_id` خالی هنگام بارگذاری به `NULL` تبدیل می‌شود.
- `paid_date` خالی هنگام بارگذاری به `NULL` تبدیل می‌شود.
- مبالغ عدد صحیح و برحسب ریال هستند.
- همه فایل‌ها پیش از ورود به SQL Server از اعتبارسنجی جامع عبور می‌کنند.

## Microsoft SQL Server و SSMS

نسخه SQL Server:

```text
Microsoft SQL Server 2025 Standard Developer Edition
Microsoft SQL Server 2025 (RTM)
17.0.1000.7
```

نسخه SSMS:

```text
SQL Server Management Studio 22
Version 22.9.2
```

مسیر فایل اجرایی SSMS:

```text
C:\Program Files\Microsoft SQL Server Management Studio 22\Release\Common7\IDE\SSMS.exe
```

دستور اجرای SSMS:

```powershell
& "C:\Program Files\Microsoft SQL Server Management Studio 22\Release\Common7\IDE\SSMS.exe"
```

تنظیمات اتصال موفق:

```text
Server Name: localhost
Authentication: Windows Authentication
Encrypt: Mandatory
Trust Server Certificate: Enabled
Database Name: <default>
```

درایور مورد استفاده:

```text
ODBC Driver 18 for SQL Server (64-bit)
```

Power BI Report Server عمداً نصب نشده است. Power BI Desktop نیز هنوز نصب نشده و باید در مرحله بعد نصب شود.

## دیتابیس عملیاتی

نام دیتابیس:

```text
autoparts_sales_intelligence
```

Schemaهای عملیاتی:

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
- هر سفارش به مشتری و نماینده فروش متصل است و ممکن است کمپین داشته باشد.
- اقلام سفارش به سفارش و محصول متصل‌اند.
- پرداخت با ترکیب `order_id + customer_id` به همان سفارش و مشتری متصل است.

## فایل‌های ساخت و اصلاح دیتابیس

### `sql/01_create_database.sql`

دیتابیس را فقط در صورت نبودن آن می‌سازد.

### `sql/02_create_schema.sql`

چهار Schema عملیاتی و هشت جدول را همراه با کلیدهای اصلی، کلیدهای خارجی، قیدهای یکتا، مقادیر پیش‌فرض و قواعد کسب‌وکار می‌سازد.

### `sql/03_expand_product_status.sql`

اندازه ستون `inventory.products.status` را از `NVARCHAR(20)` به `NVARCHAR(30)` افزایش می‌دهد تا مقدار `Temporarily Unavailable` بدون بریدگی ذخیره شود.

## بارگذاری داده به SQL Server

اسکریپت:

```text
src/load_data_to_sql_server.py
```

دستور:

```powershell
python src/load_data_to_sql_server.py
```

وظایف اسکریپت:

- بررسی نام و ترتیب ستون‌های CSV پیش از تغییر دیتابیس.
- تبدیل تاریخ‌ها، اعداد، مقادیر منطقی و مقدارهای خالی.
- اتصال با Windows Authentication و ODBC Driver 18.
- پاک‌سازی داده قبلی در ترتیب معکوس وابستگی‌ها.
- ورود داده جدید در ترتیب صحیح کلیدهای خارجی.
- اجرای کل عملیات در یک تراکنش.
- اجرای `rollback` کامل در صورت خطا.
- مقایسه تعداد رکورد هر CSV با جدول SQL پیش از `commit`.

ترتیب ورود:

1. `sales.sales_representatives`
2. `sales.customers`
3. `inventory.products`
4. `marketing.campaigns`
5. `marketing.campaign_targets`
6. `sales.sales_orders`
7. `sales.sales_order_lines`
8. `finance.payments`

آخرین اجرا موفق بوده است:

```text
DATA LOAD COMPLETED SUCCESSFULLY
All CSV and SQL Server row counts match.
```

هر هشت جدول پر هستند و مجموعاً 43,450 رکورد دارند.

## خطاهای مهمی که رفع شدند

### نبودن `pyodbc`

پیام:

```text
ModuleNotFoundError: No module named 'pyodbc'
```

علت: کتابخانه در Python فعال پروژه نصب نبود. نسخه `5.3.0` در محیط مجازی نصب و در `requirements.txt` ثبت شد.

### محدودیت بافر `fast_executemany`

پیام:

```text
String data, right truncation: length 46 buffer 40
```

علت: بافر براساس یک رشته کوتاه‌تر محدود شده بود. `fast_executemany` در نسخه فعلی Loader غیرفعال شد.

### کوچک‌بودن ستون وضعیت محصول

پیام SQL Server:

```text
String or binary data would be truncated in table
'inventory.products', column 'status'.
```

علت: طول `Temporarily Unavailable` از `NVARCHAR(20)` بیشتر بود. فایل `03_expand_product_status.sql` ستون را به `NVARCHAR(30)` افزایش داد.

به‌دلیل استفاده از تراکنش، اجرای ناموفق هیچ جدول نیمه‌پری باقی نگذاشت.

## لایه تحلیلی SQL

Schema تحلیلی زیر ساخته شده است:

```text
analytics
```

این Schema، Viewهای تحلیلی را از جدول‌های عملیاتی جدا نگه می‌دارد.

### فایل پایه: `sql/04_create_analytics_views.sql`

این فایل قابل‌تکرار است و دو View پایه می‌سازد.

#### `analytics.vw_sales_detail`

- دانه‌بندی: یک ردیف به‌ازای هر قلم سفارش.
- تعداد ردیف: 25,000.
- اتصال سفارش به مشتری، نماینده فروش، محصول و کمپین.
- محاسبه تعداد خالص، فروش ناخالص، تخفیف، مبلغ پیش از مرجوعی، مبلغ مرجوعی و فروش خالص.

#### `analytics.vw_order_summary`

- دانه‌بندی: یک ردیف به‌ازای هر سفارش.
- تعداد ردیف: 8,000.
- شامل مشخصات مشتری، نماینده، کمپین و وضعیت پرداخت.
- شامل مجموع اقلام، تعداد سفارش و مرجوعی، فروش و اختلاف فاکتور.
- `invoice_variance_amount` برای تمام سفارش‌ها صفر است.
- 719 سفارش حداقل یک قلم مرجوعی دارند.

### فایل مدیریتی: `sql/05_create_business_views.sql`

این فایل شش View مدیریتی می‌سازد:

| View | دانه‌بندی | تعداد ردیف |
| --- | --- | ---: |
| `analytics.vw_monthly_sales` | یک ردیف برای هر ماه | 24 |
| `analytics.vw_customer_performance` | یک ردیف برای هر مشتری | 500 |
| `analytics.vw_product_performance` | یک ردیف برای هر محصول | 300 |
| `analytics.vw_sales_rep_performance` | یک ردیف برای هر نماینده | 12 |
| `analytics.vw_campaign_performance` | یک ردیف برای هر کمپین | 12 |
| `analytics.vw_payment_status_summary` | یک ردیف برای هر وضعیت پرداخت | 3 |

شاخص‌های آماده‌شده شامل موارد زیر هستند:

- تعداد سفارش و مشتری یکتا.
- فروش ناخالص، تخفیف، مرجوعی و فروش خالص.
- بهای خالص، سود ناخالص و حاشیه سود.
- متوسط ارزش سفارش.
- نرخ تخفیف و نرخ مرجوعی.
- عملکرد و تحقق هدف نمایندگان فروش.
- قیف کمپین، نرخ تحویل، تعامل و تبدیل.
- فروش منتسب به کمپین، ROAS و هزینه هر تبدیل.
- مبالغ سررسیدگذشته و وصول‌نشده مشتریان.
- تعداد و مبلغ پرداخت‌ها براساس وضعیت.

## اعداد مالی کنترل‌شده

خروجی `analytics.vw_sales_detail`:

```text
detail_rows:            25,000
distinct_orders:         8,000
ordered_units:         437,428
returned_units:          3,811
gross_sales_amount:  17,943,838,600,000 IRR
discount_amount:      1,378,221,538,000 IRR
return_amount:          142,683,084,000 IRR
net_sales_amount:    16,422,933,978,000 IRR
```

رابطه مالی تأییدشده:

```text
Gross Sales - Discount - Returns = Net Sales
17,943,838,600,000 - 1,378,221,538,000 - 142,683,084,000
= 16,422,933,978,000 IRR
```

مجموع فروش خالص در تمام Viewهای زیر دقیقاً برابر `16,422,933,978,000` ریال است:

```text
analytics.vw_order_summary
analytics.vw_monthly_sales
analytics.vw_customer_performance
analytics.vw_product_performance
analytics.vw_sales_rep_performance
analytics.vw_payment_status_summary
```

## اعتبارسنجی لایه تحلیلی

فایل:

```text
sql/06_validate_analytics_layer.sql
```

این فایل 17 کنترل خودکار انجام می‌دهد:

- تطبیق تعداد ردیف Viewهای پایه با جدول‌های منبع.
- حضور تمام مشتریان، محصولات، نمایندگان، کمپین‌ها و وضعیت‌های پرداخت.
- حضور تمام 24 ماه سفارش.
- نبود اختلاف در فرمول مالی هر قلم سفارش.
- نبود اختلاف مبلغ فاکتور و فروش خالص هر سفارش.
- نبود کلید تحلیلی ضروری خالی.
- تطبیق مجموع فروش در Viewهای مختلف.
- تطبیق 144 سفارش منتسب به کمپین با جدول سفارش‌ها.

آخرین اجرا:

```text
17 checks: PASS
ANALYTICS VALIDATION PASSED: all checks succeeded.
```

## فایل آموزشی

یک راهنمای Word فارسی نیز ساخته شده است:

```text
راهنمای_آموزشی_پروژه_AutoParts.docx
```

این فایل مفاهیم PowerShell، Python، محیط مجازی، Git، CSV، SQL Server، نوع داده، قیدها، تراکنش، ODBC، خطایابی و Queryهای پایه را براساس همین پروژه آموزش می‌دهد. فایل خارج از مخزن پروژه نگهداری شده است.

## وضعیت فعلی فایل‌ها و Git

سه فایل لایه تحلیلی در Commit زیر ثبت و به GitHub ارسال شده‌اند:

```text
ee3a5e0 feat: add validated SQL analytics layer
```

فایل‌ها:

```text
sql/04_create_analytics_views.sql
sql/05_create_business_views.sql
sql/06_validate_analytics_layer.sql
```

پس از Push:

```text
On branch main
Your branch is up to date with 'origin/main'.
nothing to commit, working tree clean
```

## مراحل کامل‌شده که نباید تکرار شوند

- تولید هشت فایل داده مصنوعی.
- اعتبارسنجی جامع داده‌های خام.
- اتصال اعتبارسنجی به Pipeline تولید داده.
- ساخت و اتصال مخزن GitHub.
- نصب و تنظیم SQL Server 2025 و SSMS 22.
- ساخت دیتابیس، چهار Schema عملیاتی و هشت جدول.
- نصب و ثبت `pyodbc` و ODBC Driver 18.
- ساخت Loader تراکنشی و انتقال هر هشت CSV.
- تطبیق کامل 43,450 رکورد CSV و SQL Server.
- ساخت Schema تحلیلی `analytics`.
- ساخت دو View پایه و شش View مدیریتی.
- اجرای 17 کنترل خودکار و تأیید تمام آن‌ها.
- ثبت و Push تمام تغییرات تا Commit `ee3a5e0`.

## نقطه ادامه پروژه

لایه تحلیلی SQL کامل و اعتبارسنجی شده است. مرحله بعد:

```text
نصب Power BI Desktop، اتصال آن به SQL Server روی localhost و ساخت مدل اولیه داشبورد با Viewهای analytics
```

Power BI Desktop هنوز نصب نشده است. ابتدا باید نسخه رسمی مناسب Windows نصب شود. سپس اتصال با تنظیمات زیر ساخته شود:

```text
Server: localhost
Database: autoparts_sales_intelligence
Authentication: Windows
```

در Power BI نباید تمام جدول‌ها بدون طراحی وارد شوند. ابتدا باید درباره Viewهای موردنیاز هر صفحه داشبورد، روابط مدل، جدول تاریخ و Measureهای DAX تصمیم گرفته شود.

## پیام پیشنهادی برای Work جدید

```text
این فایل گزارش کامل پروژه autoparts-sales-intelligence تا پایان ساخت و اعتبارسنجی لایه تحلیلی SQL است. لطفاً آن را کامل بخوان، هیچ‌کدام از مراحل انجام‌شده را تکرار نکن و دقیقاً از بخش «نقطه ادامه پروژه» کار را دنبال کن. دیتابیس Microsoft SQL Server است، نه PostgreSQL. من در SQL و Power BI تازه‌کار هستم؛ بنابراین هر بار فقط یک مرحله یا یک دستور بده و منتظر خروجی من بمان. هنگام تحویل فایل، دستور بررسی کامل‌بودن آن را نیز در همان پاسخ قرار بده.
```
