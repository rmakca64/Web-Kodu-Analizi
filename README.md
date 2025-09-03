<img width="1920" height="1140" alt="Ekran görüntüsü 2025-09-03 225417" src="https://github.com/user-attachments/assets/929b1d1c-d9f5-41fc-b3f4-3ebabca4c60b" /><img width="1920" height="985" alt="image" src="https://github.com/user-attachments/assets/d51e5bc8-f062-4ab2-ad80-fbee1f3d0274" /># Proje Bağımlılık Analiz Aracı

[Türkçe](#türkçe) | [English](#english) | [中文](#中文) | [Русский](#русский)

---

<div id="türkçe">

## Proje Bağımlılık Analiz Aracı (v5.4)

Bu uygulama, Python ve Tkinter kullanılarak geliştirilmiş, web proje klasörlerindeki (PHP, HTML, JS, CSS odaklı) kullanılmayan ("yetim") dosyaları tespit etmek ve proje bağımlılıklarını haritalamak için gelişmiş statik analiz yapan bir masaüstü aracıdır.

<a href="https://postimg.cc/VrVQMKxq" target="_blank"><img src="https://i.postimg.cc/VrVQMKxq/Ekran-g-r-nt-s-2025-09-03-225417.png" alt="Ekran-g-r-nt-s-2025-09-03-225417"/></a><br/><br/>
<a href="https://postimg.cc/XXr0305Q" target="_blank"><img src="https://i.postimg.cc/XXr0305Q/Ekran-g-r-nt-s-2025-09-03-225438.png" alt="Ekran-g-r-nt-s-2025-09-03-225438"/></a><br/><br/>

### ✨ Ana Özellikler

* **Gelişmiş Statik Analiz Motoru:**
    * `include`, `require`, `href`, `src`, `action` gibi anahtar kelimelerle doğrudan bağlantıları bulur.
    * Kod içindeki metinlerde (string) geçen dosya adlarını ve dosya köklerini (`'header'` gibi) bularak dinamik kullanımları tahmin eder.
    * `config.php`, `functions.php` gibi kritik dosyaları "sezgisel" olarak her zaman aktif kabul eder.
* **İnteraktif Yetim Dosya Analizi:**
    * Potansiyel olarak kullanılmayan dosyaları ayrı bir sekmede listeler.
    * Listeden bir dosyaya tıklandığında, dosyanın neden "yetim" sayıldığını, hangi dosyalarda adının geçtiğini ve kendi kaynak kodunu gösteren çift panelli bir inceleme arayüzü sunar.
* **Görsel Bağımlılık Haritası:**
    * Analiz sonuçlarından, dosyalar arası ilişkileri gösteren interaktif ve görsel bir HTML grafiği oluşturur.
    * Oluşturulan harita üzerinde fizik ayarlarını anlık olarak değiştirme imkanı sunar.
* **Sözdizimi Vurgulama (Syntax Highlighting):**
    * İnceleme panelinde gösterilen kaynak kodları, `Pygments` kütüphanesi kullanılarak PHP, JS, CSS ve HTML için renklendirilir.
* **Kapsamlı Proje Yapılandırması:**
    * Analizden hariç tutulacak klasörleri (`vendor`, `node_modules` vb.) belirleme.
    * Analiz motorunun bulamadığı, manuel olarak aktif sayılacak dosyaları ekleme.
* **Çoklu Dil Desteği ve Raporlama:**
    * Türkçe, İngilizce, Çince ve Rusça dillerinde tam arayüz desteği.
    * Tüm analiz sonuçlarını (özet, harita ve yetim dosyalar) tek bir `.txt` dosyasına aktarma.

###  kurulum

Bu uygulamayı çalıştırmak için bilgisayarınızda Python 3.x yüklü olmalıdır.

1.  **Projeyi klonlayın (veya dosyaları indirin):**
    ```sh
    git clone [https://github.com/KULLANICI_ADINIZ/PROJE_ADINIZ.git](https://github.com/KULLANICI_ADINIZ/PROJE_ADINIZ.git)
    cd PROJE_ADINIZ
    ```

2.  **Gerekli kütüphaneleri yükleyin:**
    Uygulamanın kod renklendirme ve görsel harita özellikleri için harici paketler gereklidir.
    ```sh
    pip install Pygments pyvis
    ```

3.  **Uygulamayı çalıştırın:**
    ```sh
    python analiz_araci.py
    ```

###  nasıl kullanılır

1.  **Klasör Seçin:** "Proje Klasörünü Seç" butonu ile analiz etmek istediğiniz ana proje klasörünü seçin.
2.  **Uyarıyı Onaylayın:** Analize başlamadan önce çıkan yasal uyarıyı okuyup onaylayın.
3.  **Ayarları Yapılandırın (İsteğe Bağlı):**
    * **Hariç Tutulacak Klasörler:** Analize dahil edilmesini istemediğiniz klasörlerin adlarını (örn: `vendor, cache`) ilgili alana virgülle ayırarak yazın.
    * **Manuel Aktif Dosyalar:** Aracın dinamik yapısı nedeniyle bulamadığı ama kullanıldığını bildiğiniz dosyaları (`.htaccess` ile çağrılanlar vb.) bu alana yazın.
4.  **Analizi Başlatın:** Klasör seçimi ve onay sonrası analiz otomatik başlar. İlerleme çubuğundan süreci takip edebilirsiniz.
5.  **Sonuçları İnceleyin:**
    * **Özet ve Bağımlılık Haritası Sekmesi:** Genel istatistikleri ve dosyalar arasındaki metin tabanlı ilişki haritasını gösterir.
    * **Boştaki Dosyalar Analizi Sekmesi:** Soldaki listeden şüpheli bir dosyaya tıklayarak sağdaki panelde detaylı analizini ve kaynak kodunu görüntüleyin.
6.  **Raporları Dışarı Aktarın:**
    * **Dışarı Aktar (.txt):** Tüm raporu tek bir metin dosyası olarak kaydeder.
    * **Görsel Harita Oluştur:** İnteraktif HTML haritasını oluşturur ve tarayıcıda açar.

###  Geliştirici

Bu uygulama, **Rıza Mert AKÇA**'nın fikri ve yönlendirmeleri üzerine geliştirilmiştir.

### 📜 Lisans

Bu proje MIT Lisansı altında lisanslanmıştır.

</div>

---

<div id="english">

## Project Dependency Analysis Tool (v5.4)

This is a desktop tool developed using Python and Tkinter that performs advanced static analysis on web project folders (with a focus on PHP, HTML, JS, CSS) to identify unused ("orphan") files and map project dependencies.

![Application Screenshot](screenshot.png)

### ✨ Key Features

* **Advanced Static Analysis Engine:**
    * Finds direct links with keywords like `include`, `require`, `href`, `src`, `action`.
    * Guesses dynamic usages by finding filenames and file roots (e.g., `'header'`) within code strings.
    * "Intuitively" considers critical files like `config.php`, `functions.php` as always active.
* **Interactive Orphan File Analysis:**
    * Lists potentially unused files in a separate tab.
    * When a file is clicked, it provides a dual-pane interface showing why the file is considered an "orphan," which files mention its name, and its own source code.
* **Visual Dependency Map:**
    * Generates an interactive and visual HTML graph from the analysis results, showing inter-file relationships.
    * Offers the ability to change the physics settings of the graph in real-time.
* **Syntax Highlighting:**
    * Source code displayed in the inspection panel is colored for PHP, JS, CSS, and HTML using the `Pygments` library.
* **Comprehensive Project Configuration:**
    * Specify folders to be excluded from analysis (e.g., `vendor`, `node_modules`).
    * Manually add files to be considered active that the analysis engine might miss.
* **Multi-Language Support & Reporting:**
    * Full UI support for Turkish, English, Chinese, and Russian.
    * Export all analysis results (summary, map, and orphan files) into a single `.txt` file.

### 🚀 Installation

Python 3.x must be installed on your computer to run this application.

1.  **Clone the project (or download the files):**
    ```sh
    git clone [https://github.com/YOUR_USERNAME/YOUR_PROJECT_NAME.git](https://github.com/YOUR_USERNAME/YOUR_PROJECT_NAME.git)
    cd YOUR_PROJECT_NAME
    ```

2.  **Install required libraries:**
    External packages are required for syntax highlighting and visual graph features.
    ```sh
    pip install Pygments pyvis
    ```

3.  **Run the application:**
    ```sh
    python analiz_araci.py
    ```

### 📖 How to Use

1.  **Select Folder:** Choose the main project folder you want to analyze using the "Select Project Folder" button.
2.  **Accept Disclaimer:** Read and accept the legal disclaimer that appears before the analysis begins.
3.  **Configure Settings (Optional):**
    * **Folders to Exclude:** Enter the names of folders you want to exclude from the analysis (e.g., `vendor, cache`), separated by commas.
    * **Manual Active Files:** Enter the names of files you know are in use but might be missed by the tool (e.g., those called via `.htaccess`).
4.  **Start Analysis:** The analysis starts automatically after folder selection and confirmation. You can track the progress via the progress bar.
5.  **Review Results:**
    * **Summary & Dependency Map Tab:** Shows general statistics and a text-based map of file relationships.
    * **Orphan File Analysis Tab:** Click on a suspicious file in the left list to view its detailed analysis and source code in the right panel.
6.  **Export Reports:**
    * **Export (.txt):** Saves the complete report as a single text file.
    * **Generate Visual Map:** Creates the interactive HTML map and opens it in your browser.

### 🧑‍💻 Developer

This application was developed based on the idea and guidance of **Rıza Mert AKÇA**.

### 📜 License

This project is licensed under the MIT License.

</div>

---

<div id="中文">

## 项目依赖分析工具 (v5.4)

这是一个使用 Python 和 Tkinter 开发的桌面工具，可对 Web 项目文件夹（专注于 PHP、HTML、JS、CSS）执行高级静态分析，以识别未使用（“孤立”）的文件并映射项目依赖关系。

![应用程序截图](screenshot.png)

### ✨ 主要功能

* **高级静态分析引擎:**
    * 通过 `include`, `require`, `href`, `src`, `action` 等关键字查找直接链接。
    * 通过在代码字符串中查找文件名和文件根（例如 `'header'`）来猜测动态用法。
    * “直观地”将 `config.php`、`functions.php` 等关键文件视为始终活动。
* **交互式孤立文件分析:**
    * 在单独的选项卡中列出可能未使用的文件。
    * 单击文件时，它会提供一个双窗格界面，显示该文件被视为“孤立”的原因、哪些文件提及其名称以及其自身的源代码。
* **可视化依赖图:**
    * 根据分析结果生成一个交互式、可视化的HTML图表，显示文件间的关系。
    * 能够实时更改图表的物理设置。
* **语法高亮:**
    * 使用 `Pygments` 库为检查面板中显示的 PHP、JS、CSS 和 HTML 源代码着色。
* **全面的项目配置:**
    * 指定要从分析中排除的文件夹（例如 `vendor`, `node_modules`）。
    * 手动添加分析引擎可能遗漏的、要视为活动的文件。
* **多语言支持与报告:**
    * 完整的土耳其语、英语、中文和俄语用户界面支持。
    * 将所有分析结果（摘要、图表和孤立文件）导出为单个 `.txt` 文件。

### 🚀 安装

您的计算机上必须安装 Python 3.x 才能运行此应用程序。

1.  **克隆项目（或下载文件）:**
    ```sh
    git clone [https://github.com/YOUR_USERNAME/YOUR_PROJECT_NAME.git](https://github.com/YOUR_USERNAME/YOUR_PROJECT_NAME.git)
    cd YOUR_PROJECT_NAME
    ```

2.  **安装所需库:**
    语法高亮和可视化图表功能需要外部软件包。
    ```sh
    pip install Pygments pyvis
    ```

3.  **运行应用程序:**
    ```sh
    python analiz_araci.py
    ```

### 📖 如何使用

1.  **选择文件夹:** 使用“选择项目文件夹”按钮选择您要分析的主项目文件夹。
2.  **接受免责声明:** 在分析开始前，阅读并接受出现的法律免责声明。
3.  **配置设置 (可选):**
    * **要排除的文件夹:** 输入您希望从分析中排除的文件夹名称（例如 `vendor, cache`），用逗号分隔。
    * **手动激活的文件:** 输入您知道正在使用但工具可能遗漏的文件名（例如通过 `.htaccess` 调用的文件）。
4.  **开始分析:** 选择文件夹并确认后，分析将自动开始。您可以通过进度条跟踪进度。
5.  **审查结果:**
    * **摘要和依赖图选项卡:** 显示常规统计信息和基于文本的文件关系图。
    * **孤立文件分析选项卡:** 在左侧列表中单击可疑文件，以在右侧面板中查看其详细分析和源代码。
6.  **导出报告:**
    * **导出 (.txt):** 将完整报告保存为单个文本文件。
    * **生成可视化图:** 创建交互式HTML图并用浏览器打开它。

### 🧑‍💻 开发者

此应用程序是根据 **Rıza Mert AKÇA** 的想法和指导开发的。

### 📜 许可证

该项目根据 MIT 许可证授权。

</div>

---

<div id="русский">

## Инструмент анализа зависимостей проекта (v5.4)

Это настольный инструмент, разработанный с использованием Python и Tkinter, который выполняет расширенный статический анализ папок веб-проектов (с акцентом на PHP, HTML, JS, CSS) для выявления неиспользуемых («изолированных») файлов и картирования зависимостей проекта.

![Снимок экрана приложения](screenshot.png)

### ✨ Ключевые особенности

* **Продвинутый движок статического анализа:**
    * Находит прямые ссылки с ключевыми словами, такими как `include`, `require`, `href`, `src`, `action`.
    * Предполагает динамическое использование, находя имена файлов и их корни (например, `'header'`) в строковых литералах кода.
    * «Интуитивно» считает критически важные файлы, такие как `config.php`, `functions.php`, всегда активными.
* **Интерактивный анализ изолированных файлов:**
    * Перечисляет потенциально неиспользуемые файлы в отдельной вкладке.
    * При нажатии на файл предоставляет двухпанельный интерфейс, показывающий, почему файл считается «изолированным», какие файлы упоминают его имя, и его собственный исходный код.
* **Визуальная карта зависимостей:**
    * Генерирует интерактивный и визуальный HTML-граф из результатов анализа, показывающий межфайловые отношения.
    * Предлагает возможность изменять физические настройки графа в режиме реального времени.
* **Подсветка синтаксиса:**
    * Исходный код, отображаемый на панели инспекции, раскрашивается для PHP, JS, CSS и HTML с использованием библиотеки `Pygments`.
* **Комплексная конфигурация проекта:**
    * Указание папок для исключения из анализа (например, `vendor`, `node_modules`).
    * Ручное добавление файлов, которые следует считать активными, но которые мог пропустить движок анализа.
* **Многоязычная поддержка и отчетность:**
    * Полная поддержка пользовательского интерфейса на турецком, английском, китайском и русском языках.
    * Экспорт всех результатов анализа (сводка, карта и изолированные файлы) в один файл `.txt`.

### 🚀 Установка

Для запуска этого приложения на вашем компьютере должен быть установлен Python 3.x.

1.  **Клонируйте проект (или скачайте файлы):**
    ```sh
    git clone [https://github.com/YOUR_USERNAME/YOUR_PROJECT_NAME.git](https://github.com/YOUR_USERNAME/YOUR_PROJECT_NAME.git)
    cd YOUR_PROJECT_NAME
    ```

2.  **Установите необходимые библиотеки:**
    Для функций подсветки синтаксиса и визуального графа требуются внешние пакеты.
    ```sh
    pip install Pygments pyvis
    ```

3.  **Запустите приложение:**
    ```sh
    python analiz_araci.py
    ```

### 📖 Как использовать

1.  **Выберите папку:** С помощью кнопки «Выбрать папку проекта» выберите основную папку проекта, которую вы хотите проанализировать.
2.  **Примите отказ от ответственности:** Прочтите и примите юридический отказ от ответственности, который появляется перед началом анализа.
3.  **Настройте параметры (необязательно):**
    * **Папки для исключения:** Введите имена папок, которые вы хотите исключить из анализа (например, `vendor, cache`), через запятую.
    * **Активные файлы вручную:** Введите имена файлов, которые, как вы знаете, используются, но могут быть пропущены инструментом (например, вызываемые через `.htaccess`).
4.  **Начните анализ:** Анализ начинается автоматически после выбора папки и подтверждения. Вы можете отслеживать процесс с помощью индикатора выполнения.
5.  **Просмотрите результаты:**
    * **Вкладка «Сводка и карта зависимостей»:** Показывает общую статистику и текстовую карту файловых отношений.
    * **Вкладка «Анализ изолированных файлов»:** Щелкните подозрительный файл в левом списке, чтобы просмотреть его подробный анализ и исходный код на правой панели.
6.  **Экспортируйте отчеты:**
    * **Экспорт (.txt):** Сохраняет полный отчет в виде одного текстового файла.
    * **Создать визуальную карту:** Создает интерактивную HTML-карту и открывает ее в вашем браузере.

### 🧑‍💻 Разработчик

Это приложение было разработано на основе идеи и под руководством **Rıza Mert AKÇA**.

### 📜 Лицензия

Этот проект лицензирован в соответствии с лицензией MIT.

</div>
