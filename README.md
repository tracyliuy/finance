# Finance Project

A Python-based financial analysis and trading strategy project that focuses on implementing and backtesting various trading strategies, with a current emphasis on Bollinger Bands strategy.

## Features

- Historical data fetching and storage
- Bollinger Bands calculation and analysis
- Backtesting framework for trading strategies
- Support for multiple timeframes (daily and weekly)
- Database integration for data persistence
- Comprehensive logging system

## Project Structure

```
finance/
├── bollingerBands/           # Bollinger Bands strategy implementation
│   ├── config/              # Configuration files
│   ├── models.py            # Data models
│   ├── strategy.py          # Strategy implementation
│   └── run_backtest.py      # Backtesting script
├── common/                  # Common utilities
│   ├── database/           # Database related code
│   └── config.py           # Common configuration
├── logs/                    # Log files
└── requirements.txt         # Project dependencies
```

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/finance.git
cd finance
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the project root with the following variables:
```
DB_HOST=your_db_host
DB_PORT=your_db_port
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=your_db_name
```

## Usage

1. Generate historical Bollinger Bands data:
```bash
PYTHONPATH=$PYTHONPATH:. python -m bollingerBands.generate_historical_bollinger_bands
```

2. Run backtesting:
```bash
PYTHONPATH=$PYTHONPATH:. python -m bollingerBands.run_backtest
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 