# Author: Cilas Cavalcanti
# Email: cilas.acms@gmail.com


import os
import shutil
from pathlib import Path
import sys
import pprint
import time
import csv
import sqlite3
import logging
from lxml import etree
from lxml import objectify
import xml.etree.ElementTree as ET
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                    filename='logs/processa-edocs.log', level=logging.DEBUG)


class ProcessaEdocs(object):
    """
     Classe responsável por processar arquivos xml de notas fiscais eletrônicas
    """
    def __init__(self, data={}):
        self.data = data

    def decompor_chave(self, chave, elemento):
        chave = str(chave)
        if len(chave) == 44:
            cUF = chave[0:2]
            AAMM = chave[2:6]
            CNPJ = chave[6:20]
            mod = chave[20:22]
            serie = chave[22:25]
            nNF = chave[25:34]
            tpEmis = chave[34:35]
            cNF = chave[35:43]
            cDV = chave[43:44]
            chave_decomposta = {'cUF': cUF, 'AAMM': AAMM, 'CNPJ': CNPJ, 'mod': mod,
                                'serie': serie, 'nNF': nNF, 'tpEmis': tpEmis, 'cNF': cNF, 'cDV': cDV}
            return chave_decomposta[elemento]
        else:
            print('chave inválida, pois tem apenas ', len(chave), ' caracteres')
        return None

    def ajusta_cancelados(self):
        conn_sqlite = sqlite3.connect('database.db')
        cur = conn_sqlite.cursor()
        consulta = cur.execute(
            "SELECT chave_nfe FROM edocs where tipo_xml='evento' and status=135")

        for chave in consulta.fetchall():
            autorizada = cur.execute(
                "SELECT * FROM edocs where chave_nfe=:chave_nfe and tipo_xml='nfeProc' and situacao_nfe='N'", {'chave_nfe': chave[0]})
            if not isinstance(autorizada.fetchall(), type(None)):
                cur.execute(
                    "update edocs set situacao_nfe='C', status=135 where chave_nfe=:chave_nfe and tipo_xml='nfeProc' and situacao_nfe='N'", {
                        'chave_nfe': chave[0]}
                )
                cur.execute(
                    "update products set status='C' where products.chave_nfe=(select edocs.chave_nfe from edocs where edocs.situacao_nfe='C')"
                )

        conn_sqlite.commit()
        conn_sqlite.close()

    def carrega_xml(self, path):
        # retorna as tags a partir da tag root trasnformadas em objetos
        try:
            parse = etree.parse(path)
            root = objectify.fromstring(etree.tostring(parse))
            return root
        except Exception as e:
            print(logging.error(e))

    def salva_no_db(self):
        def insert_in_db(cursor, edoc):
            cursor.execute("insert into edocs values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                           (
                               int(edoc['emitente']),
                               str(edoc['versao_xml']),
                               int(edoc['modelo_nfe']),
                               str(edoc['data_emissao_nfe']),
                               int(edoc['numero_nfe']),
                               int(edoc['serie']),
                               str(edoc['chave_nfe']),
                               str(edoc['path_xml']),
                               str(edoc['destinatario']),
                               float(edoc['valor_total']),
                               int(edoc['status']),
                               int(edoc['codigo_venda']),
                               str(edoc['situacao_nfe']) if 'situacao_nfe' in edoc else "#",
                               str(edoc['tipo_xml'])
                           ))
            try:
                for product in edoc['products']:
                    print(edoc['products'])                    
                    cursor.execute("insert into products values (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                               (
                                   str(edoc['chave_nfe']),
                                   int(product),
                                   str(edoc['products'][product]['code']),
                                   str(edoc['products'][product]['name']),
                                   int(edoc['products'][product]['ncm']) if 'ncm' in edoc['products'][product] else 0,
                                   str(edoc['products'][product]['unit']),
                                   str(edoc['products'][product]['quantity']),
                                   float(edoc['products'][product]['total']),
                                   str('N'),

                               ))
            except Exception as e:
               print(e)

        conn_sqlite = sqlite3.connect('database.db')

        for edoc in self.data.values():
            cur = conn_sqlite.cursor()
            insert_in_db(cur, edoc)
            conn_sqlite.commit()
        conn_sqlite.close()

    def pega_dados_xml(self, root, path):
        dados = {}
        products = {}
        if root.tag == '{http://www.portalfiscal.inf.br/nfe}NFe':
            doc = root
            dados['tipo_xml'] = 'NFe'
            dados['emitente'] = doc.infNFe.emit.CNPJ
            dados['versao_xml'] = doc.infNFe.get('versao')
            dados['modelo_nfe'] = doc.infNFe.ide.mod
            dados['data_emissao_nfe'] = doc.infNFe.ide.dhEmi
            dados['numero_nfe'] = doc.infNFe.ide.nNF
            dados['serie'] = doc.infNFe.ide.serie
            dados['codigo_venda'] = doc.infNFe.ide.cNF
            dados['chave_nfe'] = doc.infNFe.get('Id')[3:]
            dados['path_xml'] = path
            dados['valor_total'] = doc.infNFe.total.ICMSTot.vNF
            dados['status'] = 0
            dados['situacao_nfe'] = 'C'
            dados['destinatario'] = ''
            for e in doc.infNFe.iterchildren():
                if e.tag == '{http://www.portalfiscal.inf.br/nfe}det':
                    products[e.get('nItem')] = {
                        'code_sale': dados['codigo_venda'],
                        'code': e.prod.cProd,
                        'name': e.prod.xProd,
                        'ncm': e.prod.NCM,
                        'unit': e.prod.uCom,
                        'quantity': e.prod.qCom,
                        'total': e.prod.vProd,
                    }
            dados['products'] = products
            return dados

        #  Nota Normal
        if root.tag == '{http://www.portalfiscal.inf.br/nfe}nfeProc':
            doc = root
            dados['tipo_xml'] = 'nfeProc'
            dados['emitente'] = doc.NFe.infNFe.emit.CNPJ
            dados['versao_xml'] = doc.NFe.infNFe.get('versao')
            dados['modelo_nfe'] = doc.NFe.infNFe.ide.mod

            try:
                dados['data_emissao_nfe'] = doc.NFe.infNFe.ide.dhEmi
            except Exception as e:
                pass
            try:
                dados['data_emissao_nfe'] = doc.NFe.infNFe.ide.dEmi
            except Exception as e:
                pass
            # Destinatário
            dados['destinatario'] = ''
            try:
                dados['destinatario'] = doc.NFe.infNFe.dest.CPF
            except Exception as e:
                pass
            try:
                dados['destinatario'] = doc.NFe.infNFe.dest.CNPJ
            except Exception as e:
                pass

            dados['numero_nfe'] = doc.NFe.infNFe.ide.nNF
            dados['serie'] = doc.NFe.infNFe.ide.serie
            dados['codigo_venda'] = doc.NFe.infNFe.ide.cNF
            dados['chave_nfe'] = doc.NFe.infNFe.get('Id')[3:]
            dados['path_xml'] = path
            dados['valor_total'] = doc.NFe.infNFe.total.ICMSTot.vNF
            dados['status'] = doc.protNFe.infProt.cStat
            dados['situacao_nfe'] = 'N'
            for e in doc.NFe.infNFe.iterchildren():
                if e.tag == '{http://www.portalfiscal.inf.br/nfe}det':
                    products[e.get('nItem')] = {
                        'code_sale': dados['codigo_venda'],
                        'code': e.prod.cProd,
                        'name': e.prod.xProd,
                        # 'ncm': if e.prod.NCM else None,
                        'unit': e.prod.uCom,
                        'quantity': e.prod.qCom,
                        'total': e.prod.vProd,
                    }
            dados['products'] = products
            return dados

        if root.tag == '{http://www.portalfiscal.inf.br/nfe}procEventoNFe':
            doc = root
            dados['emitente'] = doc.evento.infEvento.CNPJ
            dados['tipo_xml'] = 'evento'
            dados['evento'] = doc.evento.infEvento.detEvento.descEvento
            dados['data_emissao_nfe'] = doc.evento.infEvento.dhEvento
            dados['versao_xml'] = doc.get('versao')
            dados['chave_nfe'] = doc.evento.infEvento.chNFe
            dados['path_xml'] = path
            dados['destinatario'] = ''
            dados['modelo_nfe'] = 0
            dados['numero_nfe'] = int(self.decompor_chave(
                dados['chave_nfe'], 'nNF'))

            dados['serie'] = self.decompor_chave(
                dados['chave_nfe'], 'serie')

            dados['codigo_venda'] = int(self.decompor_chave(
                dados['chave_nfe'], 'cNF'))

            dados['valor_total'] = 0

            dados['status'] = doc.retEvento.infEvento.cStat

            if dados['status'] == 135:
                dados['situacao_nfe'] = 'C'
            return dados

    def walk(self, dirname):
        """Prints the names of all files in dirname and its subdirectories.

        This is the exercise solution, which uses os.walk.

        dirname: string name of directory
        """
        self.all_nfe = dict()
        for file in os.listdir(dirname):
            path = os.path.join(dirname, file)
            if os.path.isfile(path):
                if file.endswith('.xml'):
                    root = self.carrega_xml(path)
                    if root is not None:
                        dados = self.pega_dados_xml(root, path)
                        if dados is not None:
                            self.data[file] = dados

            else:
                self.walk(path)

    def create_csv_file(self):
        # open a file for writing
        nfe_data = open('NFeData.csv', 'w')
        # create the csv writer object
        csvwriter = csv.writer(nfe_data, delimiter=';', lineterminator='\n')
        count = 0
        for nfe in self.data.values():
            if count == 0:
                header = nfe.keys()
                csvwriter.writerow(header)
                count += 1
            csvwriter.writerow(nfe.values())

        nfe_data.close()
        if os.path.isfile('NFeData.csv'):
            print('Arquivo NFeData.csv criado com sucesso!')


if __name__ == '__main__':
    print('Criando banco de dados para armazenar as informações...')

    if os.path.isfile('database.db'):
        # Criando cópia de seguranca do banco de dados
        shutil.copy('database.db', 'bkp_database.db')
        # Exclui o arquivo de banco de dados do sqlite
        os.unlink('database.db')

    # Cria um novo arquivo
    Path('database.db').touch()
    conn_sqlite = sqlite3.connect('database.db')
    print('Sqlite version: ', sqlite3.version)

    # cria tabela para salvar os dados da nota
    conn_sqlite.execute('''
                            CREATE TABLE edocs (
                                emitente INTEGER,
                            versao_xml TEXT,
                            modelo_nfe INTEGER,
                            data_emissao_nfe TEXT,
                            numero_nfe INTEGER,
                            serie INTEGER,
                            chave_nfe TEXT,
                            path_xml TEXT,
                            destinatario TEXT,
                            valor_total FLOAT,
                            status INTEGER,
                            codigo_venda INTEGER,
                            situacao_nfe TEXT,
                            tipo_xml TEXT 
                            );
                        ''')
    # cria tabela para salvar os dados do produto
    conn_sqlite.execute('''
                            CREATE TABLE products (
                            `chave_nfe`	TEXT,
                            `item`	INTEGER,
                            `code`	TEXT,
                            `name`	TEXT,
                            `ncm`	INTEGER,
                            `unit`	TEXT,
                            `quantity`	TEXT,
                            `total`	FLOAT,
                            `status`	TEXT
                            );
                        ''')
    conn_sqlite.commit()
    conn_sqlite.close()
    print('Feito!')
    try:
        eDoc = ProcessaEdocs()
        print('''
                -------------------------------
               |   ANALISANDO ARQUIVOS XML!    |
                -------------------------------
        ''')
        eDoc.walk('xml')
        print(len(eDoc.data), 'xml analisados.')
        print('Done!')
        print('''
                -------------------------------
               |        SALVANDO DADOS!        |
                -------------------------------
        ''')
        eDoc.salva_no_db()

        print('Done!')
        print('''
                -------------------------------------
               |        Ajustando Cancelados!        |
                -------------------------------------
        ''')
        eDoc.ajusta_cancelados()
        print('Done!')

    except KeyboardInterrupt:
        print('Bye! ;)')
