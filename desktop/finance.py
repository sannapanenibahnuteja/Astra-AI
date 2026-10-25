"""Optional local manual ledger. Integer money, no bank/model/network access."""
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import calendar
import re
import uuid
import json

CURRENCIES = ('INR', 'USD', 'EUR', 'GBP')
CATEGORIES = ('Food', 'Transport', 'Shopping', 'Bills', 'Health', 'Education', 'Entertainment', 'Travel', 'Other')


def widget_request(value):
    """Explicit visibility only; no financial records read or actions inferred."""
    if not isinstance(value,str):
        return None
    value=value.strip().casefold().rstrip('.!?')
    value=re.sub(r'^(?:(?:hey|okay|ok)[, ]+)?bob[, ]+','',value)
    value=re.sub(r'^please\s+','',value)
    match=re.fullmatch(r'(show|hide|enable|disable|turn on|turn off) (?:the |my )?(?:finance|money) widget',value)
    return match[1] in ('show','enable','turn on') if match else None


def decimal(value, places=2, zero=False):
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        raise ValueError('Enter a valid number.')
    try:
        result = Decimal(str(value))
        if not result.is_finite() or result < 0 or (not zero and result == 0) or result > 100000000:
            raise ValueError('Enter a positive number up to 100,000,000.')
        if result != result.quantize(Decimal(10) ** -places):
            raise ValueError(f'Use at most {places} decimal places.')
        return result
    except InvalidOperation:
        raise ValueError('Enter a valid number.') from None


def cents(value, zero=False):
    return int(decimal(value, zero=zero) * 100)


def month_value(value):
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}', value):
        raise ValueError('Choose a month.')
    try:
        date.fromisoformat(value + '-01')
    except ValueError:
        raise ValueError('Choose a valid month.') from None
    return value


def text(value, maximum, required=True):
    if not isinstance(value, str) or len(value.strip()) > maximum or (required and not value.strip()):
        raise ValueError('Enter a valid name or description.')
    return value.strip()


class Finance:
    def __init__(self, store):
        self.store = store
        if not store.settings().get('finance_enabled'):
            raise ValueError('Enable the Finance widget first.')
        with store.connect() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS finance_transactions (
                    id TEXT PRIMARY KEY, day TEXT NOT NULL, kind TEXT NOT NULL,
                    amount INTEGER NOT NULL, category TEXT NOT NULL, description TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS finance_budgets (month TEXT PRIMARY KEY, amount INTEGER NOT NULL);
                CREATE TABLE IF NOT EXISTS finance_holdings (
                    id TEXT PRIMARY KEY, name TEXT NOT NULL, units TEXT NOT NULL,
                    cost INTEGER NOT NULL, price INTEGER NOT NULL, price_date TEXT NOT NULL);
            ''')

    def currency(self, currency):
        if not isinstance(currency, str) or currency not in CURRENCIES:
            raise ValueError('Choose INR, USD, EUR or GBP.')
        with self.store.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row=db.execute('SELECT value FROM settings WHERE key=?',('finance_currency',)).fetchone()
            current=json.loads(row['value']) if row else 'INR'
            populated = any(db.execute('SELECT 1 FROM ' + table + ' LIMIT 1').fetchone()
                            for table in ('finance_transactions', 'finance_holdings', 'finance_budgets'))
            if currency != current and populated:
                raise ValueError('Currency cannot change while finance records or budgets exist. No automatic currency conversion is performed.')
            db.execute('INSERT OR REPLACE INTO settings VALUES (?,?)', ('finance_currency',json.dumps(currency)))
        return currency

    def transaction(self, values):
        if not isinstance(values, dict) or set(values) - {'id', 'day', 'kind', 'amount', 'category', 'description'}:
            raise ValueError('Invalid transaction fields.')
        try:
            day = date.fromisoformat(values.get('day', '')).isoformat()
        except (ValueError, TypeError):
            raise ValueError('Choose a valid transaction date.') from None
        kind = values.get('kind')
        if kind not in ('expense', 'income', 'transfer'):
            raise ValueError('Choose expense, income or transfer.')
        category = values.get('category', 'Other')
        if category not in CATEGORIES:
            raise ValueError('Choose an available category.')
        amount = cents(values.get('amount'))
        description = text(values.get('description', ''), 180)
        identity = values.get('id')
        if identity is not None:
            identity = text(identity, 40)
        with self.store.connect() as db:
            if identity:
                if not db.execute('SELECT 1 FROM finance_transactions WHERE id=?', (identity,)).fetchone():
                    raise ValueError('Transaction no longer exists.')
                db.execute('UPDATE finance_transactions SET day=?,kind=?,amount=?,category=?,description=? WHERE id=?',
                           (day, kind, amount, category, description, identity))
            else:
                if db.execute('SELECT COUNT(*) FROM finance_transactions').fetchone()[0] >= 100000:
                    raise ValueError('Ledger limit reached.')
                identity = uuid.uuid4().hex
                db.execute('INSERT INTO finance_transactions VALUES (?,?,?,?,?,?)', (identity, day, kind, amount, category, description))
        return identity

    def delete(self, kind, identity):
        if kind not in ('transaction', 'holding'):
            raise ValueError('Choose a transaction or holding.')
        identity = text(identity, 40)
        table = 'finance_transactions' if kind == 'transaction' else 'finance_holdings'
        with self.store.connect() as db:
            if db.execute('DELETE FROM ' + table + ' WHERE id=?', (identity,)).rowcount != 1:
                raise ValueError('Record no longer exists.')
        return True

    def budget(self, month, amount):
        month = month_value(month)
        value = cents(amount, zero=True)
        with self.store.connect() as db:
            if value:
                db.execute('INSERT OR REPLACE INTO finance_budgets VALUES (?,?)', (month, value))
            else:
                db.execute('DELETE FROM finance_budgets WHERE month=?', (month,))
        return True

    def holding(self, values):
        if not isinstance(values, dict) or set(values) - {'id','name','units','cost','price','price_date'}:
            raise ValueError('Invalid holding fields.')
        name = text(values.get('name'), 80)
        units = decimal(values.get('units'), places=8)
        cost, price = cents(values.get('cost'), zero=True), cents(values.get('price'), zero=True)
        if units > 1000000 or max(units * cost, units * price) > 1000000000000:
            raise ValueError('Holding exceeds the supported value limit.')
        try:
            price_date = date.fromisoformat(values.get('price_date', '')).isoformat()
        except (TypeError, ValueError):
            raise ValueError('Choose the manual price date.') from None
        identity = values.get('id')
        if identity is not None:
            identity = text(identity, 40)
        with self.store.connect() as db:
            if identity:
                if not db.execute('SELECT 1 FROM finance_holdings WHERE id=?', (identity,)).fetchone():
                    raise ValueError('Holding no longer exists.')
                db.execute('UPDATE finance_holdings SET name=?,units=?,cost=?,price=?,price_date=? WHERE id=?',
                           (name, str(units), cost, price, price_date, identity))
            else:
                if db.execute('SELECT COUNT(*) FROM finance_holdings').fetchone()[0] >= 1000:
                    raise ValueError('Portfolio limit reached.')
                identity = uuid.uuid4().hex
                db.execute('INSERT INTO finance_holdings VALUES (?,?,?,?,?,?)', (identity, name, str(units), cost, price, price_date))
        return identity

    def snapshot(self, month=None, today=None):
        today = today or date.today()
        month = month_value(month or today.strftime('%Y-%m'))
        year, number = map(int, month.split('-'))
        first = date(year, number, 1)
        previous = date.fromordinal(first.toordinal()-1).strftime('%Y-%m') if year > 1 or number > 1 else None
        with self.store.connect() as db:
            db.execute('BEGIN')
            currency_row=db.execute('SELECT value FROM settings WHERE key=?',('finance_currency',)).fetchone()
            currency=json.loads(currency_row['value']) if currency_row else 'INR'
            totals = {r['kind']:r['total'] for r in db.execute(
                'SELECT kind,SUM(amount) total FROM finance_transactions WHERE substr(day,1,7)=? GROUP BY kind', (month,))}
            categories = [dict(r) for r in db.execute(
                "SELECT category,SUM(amount) amount FROM finance_transactions WHERE substr(day,1,7)=? AND kind='expense' GROUP BY category ORDER BY amount DESC,category", (month,))]
            budget = db.execute('SELECT amount FROM finance_budgets WHERE month=?', (month,)).fetchone()
            rows = [dict(r) for r in db.execute('SELECT * FROM finance_transactions WHERE substr(day,1,7)=? ORDER BY day DESC,rowid DESC LIMIT 250', (month,))]
            count = db.execute('SELECT COUNT(*) FROM finance_transactions WHERE substr(day,1,7)=?', (month,)).fetchone()[0]
            holdings = [dict(r) for r in db.execute('SELECT * FROM finance_holdings ORDER BY name COLLATE NOCASE,id')]
            prior = db.execute("SELECT COALESCE(SUM(amount),0) FROM finance_transactions WHERE substr(day,1,7)=? AND kind='expense'", (previous,)).fetchone()[0]
            locked = any(db.execute('SELECT 1 FROM '+table+' LIMIT 1').fetchone() for table in
                         ('finance_transactions','finance_holdings','finance_budgets'))
        expense, income = totals.get('expense', 0), totals.get('income', 0)
        limit = budget['amount'] if budget else 0
        remaining = limit - expense if limit else None
        days = calendar.monthrange(year, number)[1] - today.day + 1 if month == today.strftime('%Y-%m') else None
        insights = []
        if not count:
            insights.append('Add transactions to start seeing your spending pattern.')
        if limit:
            insights.append('Spending is over your entered monthly budget.' if remaining < 0 else 'Spending is within your entered monthly budget.')
        else:
            insights.append('Set a monthly budget to get a remaining-spend guide.')
        if categories:
            insights.append('Your largest expense category this month is ' + categories[0]['category'] + '.')
        if prior:
            insights.append('Recorded expenses are ' + ('higher' if expense > prior else 'lower' if expense < prior else 'the same') + ' compared with the full previous month. Coverage may differ.')
        for row in holdings:
            units = Decimal(row['units'])
            row['cost_total'] = int((units * row['cost']).quantize(Decimal(1), rounding=ROUND_HALF_UP))
            row['value'] = int((units * row['price']).quantize(Decimal(1), rounding=ROUND_HALF_UP))
            row['gain'] = row['value'] - row['cost_total']
        cost_total = sum(h['cost_total'] for h in holdings)
        value = sum(h['value'] for h in holdings)
        return {'enabled':True, 'currency':currency, 'currency_locked':locked, 'month':month,
                'categories':list(CATEGORIES), 'transactions':rows, 'transaction_count':count,
                'expense':expense, 'income':income, 'net':income-expense, 'transfers':totals.get('transfer',0),
                'budget':limit, 'remaining':remaining, 'days_left':days,
                'daily_guide':max(0, remaining)//days if remaining is not None and days else None,
                'category_totals':categories, 'insights':insights, 'holdings':holdings,
                'portfolio':{'cost':cost_total, 'value':value, 'gain':value-cost_total}}
