from datetime import date
import tempfile
import unittest
import time
from unittest.mock import patch
from desktop.storage import Store
from desktop.finance import Finance, cents, widget_request
from desktop.runtime import Runtime


class FinanceTests(unittest.TestCase):
    def setUp(self):
        root=tempfile.TemporaryDirectory();self.addCleanup(root.cleanup)
        self.store=Store(root.name)
        self.store.save_settings({'finance_enabled':True})
        self.finance=Finance(self.store)

    def add(self, **values):
        return self.finance.transaction({'day':'2026-10-25','kind':'expense','amount':'10.10',
            'category':'Food','description':'Fixture lunch',**values})

    def snapshot(self,month='2026-10'):
        return self.finance.snapshot(month,today=date(2026,10,25))

    def test_money_is_exact_and_invalid_amounts_rejected(self):
        self.assertEqual(cents('0.29'),29)
        self.assertEqual(cents('100000000.00'),10000000000)
        for value in ('NaN','Infinity','-1','0','1.001',True,{},'1e100000'):
            with self.subTest(value=value),self.assertRaises(ValueError):cents(value)

    def test_income_expense_and_transfers_are_separate(self):
        self.add(amount='0.10');self.add(amount='0.20')
        self.add(kind='income',amount='100')
        self.add(kind='transfer',amount='50')
        row=self.snapshot()
        self.assertEqual((row['expense'],row['income'],row['net'],row['transfers']),(30,10000,9970,5000))
        self.assertEqual(row['category_totals'],[{'category':'Food','amount':30}])

    def test_edit_and_delete_transaction(self):
        identity=self.add()
        self.add(id=identity,amount='12.35',description='Edited')
        self.assertEqual(self.snapshot()['expense'],1235)
        self.assertEqual(self.snapshot()['transactions'][0]['description'],'Edited')
        self.finance.delete('transaction',identity)
        self.assertEqual(self.snapshot()['transaction_count'],0)

    def test_month_boundaries_and_previous_month(self):
        self.add(day='2026-09-30',amount='50');self.add(day='2026-11-01',amount='90')
        self.add(amount='25')
        self.assertEqual(self.snapshot()['expense'],2500)
        self.assertTrue(any('lower' in value for value in self.snapshot()['insights']))
        self.assertEqual(self.snapshot('2026-11')['expense'],9000)
        self.assertIsNone(self.snapshot('2026-11')['days_left'])

    def test_budget_is_month_specific_and_daily_guide_includes_today(self):
        self.finance.budget('2026-10','100');self.add(amount='30')
        row=self.snapshot()
        self.assertEqual(row['remaining'],7000)
        self.assertEqual(row['days_left'],7)
        self.assertEqual(row['daily_guide'],1000)
        self.assertIsNone(self.snapshot('2026-09')['remaining'])
        self.finance.budget('2026-10','0')
        self.assertIsNone(self.snapshot()['remaining'])

    def test_overspending_does_not_show_negative_daily_allowance(self):
        self.finance.budget('2026-10','5');self.add(amount='10')
        row=self.snapshot();self.assertEqual(row['remaining'],-500)
        self.assertEqual(row['daily_guide'],0)

    def test_fractional_holdings_and_manual_valuation(self):
        identity=self.finance.holding({'name':'Fixture fund','units':'1.5','cost':'10.01','price':'12.01','price_date':'2026-10-24'})
        row=self.snapshot()
        self.assertEqual(row['portfolio'],{'cost':1502,'value':1802,'gain':300})
        self.finance.holding({'id':identity,'name':'Fixture fund','units':'2','cost':'10','price':'8','price_date':'2026-10-25'})
        self.assertEqual(self.snapshot()['portfolio']['gain'],-400)
        self.finance.delete('holding',identity)
        self.assertEqual(self.snapshot()['portfolio']['value'],0)

    def test_currency_changes_only_in_empty_ledger(self):
        self.assertEqual(self.finance.currency('USD'),'USD')
        self.add()
        with self.assertRaises(ValueError):self.finance.currency('EUR')
        self.assertEqual(self.snapshot()['currency'],'USD')
        self.assertTrue(self.snapshot()['currency_locked'])

    def test_budget_alone_locks_currency_and_removal_unlocks(self):
        self.finance.budget('2026-10','20')
        with self.assertRaises(ValueError):self.finance.currency('GBP')
        self.finance.budget('2026-10','0')
        self.assertEqual(self.finance.currency('GBP'),'GBP')

    def test_disabled_feature_refuses_access_but_retains_data(self):
        self.add()
        self.store.save_settings({'finance_enabled':False})
        with self.assertRaises(ValueError):Finance(self.store)
        self.store.save_settings({'finance_enabled':True})
        self.assertEqual(Finance(self.store).snapshot()['enabled'],True)
        self.assertEqual(self.snapshot()['expense'],1010)

    def test_display_limit_does_not_truncate_totals(self):
        for _ in range(255):self.add(amount='1')
        row=self.snapshot()
        self.assertEqual(len(row['transactions']),250)
        self.assertEqual(row['expense'],25500)
        self.assertEqual(row['transaction_count'],255)

    def test_missing_records_invalid_dates_kinds_and_fields_fail(self):
        for values in ({'id':'missing'},{'day':'2026-02-30'},{'kind':'purchase'},
                       {'amount':'-4'},{'category':'Unknown'},{'description':''},{'unexpected':'x'}):
            with self.subTest(values=values),self.assertRaises(ValueError):self.add(**values)
        with self.assertRaises(ValueError):self.finance.delete('settings','x')
        with self.assertRaises(ValueError):self.snapshot('2026-13')

    def test_invalid_or_oversized_holding_fails(self):
        values={'name':'Fixture','units':'1','cost':'1','price':'1','price_date':'2026-10-25'}
        for patch in ({'units':'0'},{'units':'1.000000001'},{'price':'NaN'},
                      {'price_date':'not-a-date'},{'units':'1000001'},{'units':'1000000','price':'100000000'}):
            with self.subTest(patch=patch),self.assertRaises(ValueError):self.finance.holding({**values,**patch})

    def test_restart_preserves_ledger(self):
        self.add()
        reopened=Finance(Store(self.store.root))
        self.assertEqual(reopened.snapshot('2026-10')['expense'],1010)


class FinanceBridgeTests(unittest.TestCase):
    def test_chat_visibility_switch_is_local_and_does_not_load_financial_records(self):
        with tempfile.TemporaryDirectory() as root:
            runtime=Runtime(root)
            try:
                identity=runtime.new_conversation()
                with patch('desktop.runtime.ChatConnection') as network:
                    for command,enabled in (('show finance widget',True),('hide finance widget',False)):
                        job=runtime.start_chat(identity,command)
                        deadline=time.monotonic()+5
                        result=runtime.poll_chat(job)
                        while not result['done'] and time.monotonic()<deadline:
                            time.sleep(.02);result=runtime.poll_chat(job)
                        self.assertTrue(result['done'])
                        self.assertFalse(result['error'])
                        self.assertEqual(runtime._store.settings()['finance_enabled'],enabled)
                    network.assert_not_called()
                with runtime._store.connect() as db:
                    self.assertFalse(db.execute("SELECT 1 FROM sqlite_master WHERE name='finance_transactions'").fetchone())
            finally:runtime._voice.close()

    def test_explicit_voice_widget_switch_only(self):
        for value in ('show my finance widget','Hey Bob, enable the money widget','please turn on finance widget'):
            self.assertIs(widget_request(value),True)
        self.assertIs(widget_request('hide finance widget'),False)
        for value in ('do not show finance widget','type hide finance widget','show finance widget and open calculator','what did I spend?',None):
            self.assertIsNone(widget_request(value))

    def test_default_off_toggle_isolated_from_audio_and_no_data_exposed_when_off(self):
        with tempfile.TemporaryDirectory() as root:
            runtime=Runtime(root)
            try:
                self.assertEqual(runtime.finance_snapshot(),{'enabled':False})
                engine=object();runtime._voice._duplex=engine
                self.assertTrue(runtime.finance_toggle(True)['finance_enabled'])
                self.assertIs(runtime._voice._duplex,engine)
                runtime._voice._duplex=None
                with self.assertRaises(ValueError):runtime.finance_toggle('yes')
                with self.assertRaises(ValueError):runtime.save_settings({'finance_currency':'USD'})
                runtime.save_settings({'finance_currency':'INR'})
                self.assertFalse(runtime.finance_toggle(False)['finance_enabled'])
            finally:
                runtime._voice._duplex=None;runtime._voice.close()


if __name__=='__main__':unittest.main()
