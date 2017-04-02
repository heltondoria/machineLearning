#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2017 
# Author: helton <helton.doria@gmail.com>
# URL: <>
# For license information, see LICENSE.TXT
import csv
import errno
import logging
import os
import sys
import xml.etree.ElementTree
import xml.parsers.expat

OUTRAS = 0

ESPORTE = 1


def safe_mkdir(path):
    """
    method responsible for create directories in a safe way.
    :param path: path to be created
    """
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def safe_open(filepath, mode='+'):
    """
    Open a file for writing, creating any parent directories if needed.

    :param filepath: full path to the file to be open
    :param mode: mode to access the file, i.e., 'r', 'w', 'x', 'a','b' and so on
    :return: An opened file, if it exists.
    """
    full_path = os.path.abspath(filepath)
    path = full_path.strip(os.path.basename(filepath))
    safe_mkdir(path)
    try:
        file = open(full_path, mode)
    except FileNotFoundError:
        file = open(full_path, 'x')
    return file


def get_logger(name, log_file):
    """
    A function that helps to create a logger that can be used anywhere.
    This function came from:
    "https://github.com/heltondoria/Systems-Engineering/blob/master/BRI/Work_1/InvertedIndex.py"

    :param name: name of the logger
    :param log_file: full path to the log file
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    # create a file handler
    handler = logging.FileHandler(log_file)
    handler.setLevel(logging.INFO)
    # create a logging format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(handler)
    logger.addHandler(stream_handler)


def read_csv(file_name=None, delimitador=None):
    """
    Carrega dados a partir de um arquivo csv
    :param file_name: nome do arquivo csv a ser carregado
    :param delimitador: delimitador usado para separar os dados (Opcional)
    :return: retorna os dados convertidos em uma lista
    """
    if delimitador is None:
        delimitador = ','

    with safe_open(filepath=file_name, mode='r') as file:
        csv.register_dialect("unix_dialect")
        reader = csv.reader(file, delimiter=delimitador)
        dataset = list()
        for line in reader:
            dataset.append(eval(line[1]))

        return dataset


def write_csv(csv_data, file_name=None):
    """
    Salva os dados em um arquivo csv
    :param file_name: nome do arquivo csv
    :param csv_data: dados a serem persistidos no arquivo csv
    """
    with safe_open(filepath=file_name, mode='w') as file:
        csv.register_dialect("unix_dialect")
        writer = csv.writer(file)
        for item in list(csv_data):
            writer.writerow([item["id"], item["classe"], item["texto"]])
        file.close()


def import_xml(filename):
    """Carrega dados a partir do arquivo xml do CETENFolha"""
    ext_tree = None
    try:
        ext_tree = xml.etree.ElementTree.parse(filename)

    except (EnvironmentError, xml.parsers.expat.ExpatError) as err:
        print("{0}: import error: {1}".format(os.path.basename(sys.argv[0]), err))
    return ext_tree


def read_data(ext_tree) -> list:
    """
        Varre o XML de entrada e transforma numa lista de dicionários no formato
        [{id: 1, classe: 1, texto: "texto"}]
        :param ext_tree árvore com registros a serem lidos
        :rtype: list
    """
    data = dict()
    dataset = list()
    for element in ext_tree.findall("ext"):
        data["id"] = int(element.get("id"))
        if str(element.get("sec")) == str("des"):
            data["classe"] = ESPORTE
        else:
            data["classe"] = OUTRAS
        for paragrafo in element.findall("p"):
            data["texto"] = ""
            for sentence in paragrafo.findall("s"):
                data["texto"] = data["texto"] + sentence.text
            data["texto"] = data["texto"].strip()
        if len(data["texto"]) > 100:
            dataset.append(data.copy())
        data.clear()
    return dataset


def filter_data(dataset: list, type: int, limit: int) -> list:
    """ Filtra os dados de um dataset através da classe do dado """
    dataset_by_type = [data for data in dataset if data["classe"] == type]
    return dataset_by_type[:limit]


tree = import_xml('./dataset/CETENFolha-1.0.xml')
dataset_list = read_data(tree)
write_csv(filter_data(dataset_list, ESPORTE, 36000), './dataset/dataset_esporte.csv')
write_csv(filter_data(dataset_list, OUTRAS, 36000), './dataset/dataset_outras.csv')
