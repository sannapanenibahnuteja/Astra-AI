import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from desktop import browser
from desktop.commands import Commands
from desktop.storage import Store
from desktop.intent import normalize, phrase_intent


class BrowserTests(unittest.TestCase):
    def test_conversational_prefixes_preserve_payload(self):
        self.assertEqual(normalize("Hey Bob, could you please just type Pull up A+B into Notepad?"), 'type Pull up A+B into Notepad')
        self.assertEqual(normalize("I'd like you to fire up calculator"), 'open calculator')
        self.assertEqual(normalize('look online for opening files'), 'search for opening files')

    def test_synonyms_and_scoped_fuzzy(self):
        self.assertEqual(phrase_intent('make it louder'), ('volume up', False))
        self.assertEqual(phrase_intent('make it loudr'), ('volume up', True))
        for phrase in ['type make it louder', 'do not make it louder', 'delete my files', 'make it clearer']:
            self.assertEqual(phrase_intent(phrase), (None, False))

    def test_edge_aliases(self):
        for phrase, target in [('refresh the page in Edge','reload'), ('Edge open another tab','new tab'),
                               ('go back a page in Edge','back'), ('in Edge, make the page bigger','zoom in'),
                               ('bring back the last tab in Edge','reopen tab')]:
            self.assertEqual(browser.parse(phrase)['target'], target)
        self.assertIsNone(browser.parse('go back'))
        self.assertEqual(browser.parse('go back', {'last_window':'Microsoft Edge'})['target'], 'back')

    def test_payloads(self):
        self.assertEqual(browser.parse('search for Cats + Dogs in Edge')['target'], 'Cats + Dogs')
        self.assertEqual(browser.parse('type A+B into the Search field in Edge')['value'], 'A+B')
        self.assertEqual(browser.parse('find Privacy on this page in Edge')['target'], 'Privacy')

    def test_url_validation(self):
        self.assertEqual(browser.validate({'action':'edge_navigate','target':'example.com'})['target'],'https://example.com')
        for url in ['javascript:alert(1)', 'data:text/html,test', 'file:///C:/test', 'https://u:p@example.com', 'https://example.com\n']:
            with self.assertRaises(ValueError): browser.validate({'action':'edge_navigate','target':url})

    def test_confirmations(self):
        self.assertTrue(browser.validate({'action':'edge_click','target':'Delete'})['confirm'])
        self.assertTrue(browser.validate({'action':'edge_shortcut','target':'close tab'})['confirm'])
        self.assertFalse(browser.validate({'action':'edge_shortcut','target':'next tab'})['confirm'])
        with self.assertRaises(ValueError): browser.validate({'action':'edge_fill','target':'Search','value':'Hello\nsubmit'})

    def test_window_identity_and_ambiguity(self):
        inventory=[{'handle':1,'title':'One','process':'msedge.exe'}, {'handle':2,'title':'Two','process':'msedge.exe'}, {'handle':3,'title':'Edge','process':'notepad.exe'}]
        with patch.object(browser.windows, 'window_inventory', return_value=inventory):
            with self.assertRaises(ValueError): browser.select_window()
            self.assertEqual(browser.select_window(preferred=2)['title'], 'Two')
            self.assertEqual(browser.select_window('One', preferred=2)['handle'],1)
            with self.assertRaises(ValueError): browser.select_window('Edge',preferred=3)

    def test_label_matching_never_chooses_duplicate(self):
        nodes=[SimpleNamespace(element_info=SimpleNamespace(name=name)) for name in ['Documentation', 'Downloads']]
        self.assertIs(browser.match_control(nodes,'Documentaton',True),nodes[0])
        with self.assertRaises(ValueError): browser.match_control(nodes+nodes,'Downloads',True)
        with self.assertRaises(ValueError): browser.match_control(nodes,'Delete everything',True)

    def test_compound_context_and_negation(self):
        with tempfile.TemporaryDirectory() as root:
            commands=Commands(Store(root))
            plan=commands.plan('in Edge open another tab and search for Python docs', 'test')
            self.assertEqual([p['action'] for p in plan], ['edge_shortcut','edge_search'])
            plan=commands.plan('Could you bring up a calculator and reduce the volume to twenty percent?', 'test')
            self.assertEqual([p['action'] for p in plan], ['open','volume'])
            self.assertEqual(plan[1]['target'], '20')
            for phrase in ["don't open Edge", 'explain how to close this tab in Edge', 'never make it louder']:
                self.assertIsNone(commands.plan(phrase,'test'))
            self.assertTrue(commands.plan('make it loudr','test')['confirm'])

    def test_literal_shortcut_metacharacters(self):
        self.assertEqual(browser.literal('A+B^C%'), 'A{+}B{^}C{%}')


if __name__ == '__main__': unittest.main()
