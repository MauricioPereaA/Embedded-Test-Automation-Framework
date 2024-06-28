# -*- coding: utf-8 -*-
# archivo de test para el modulo logger.
#aqui se añadiran todos los test relacionados con el modulo logger.

import pytest
import unittest
import logging
from logging import _nameToLevel, _levelToName
import DTAF.logger
import DTAF.config.logger_config
from DTAF.config import Config
from DTAF.logger import *
import weakref

data: dict = {
    "logger": [
        "global_logger_list", "g_error_msg", "trace", "add_trace_level", "_format_colors", "g_clear_format_code",
        "create_logger", "add_log_reg", "del_logger", "config_terminal_handler", "config_file_handler", "erase_log_reg",
        "create_logger", "add_handler"
    ]
}


@pytest.mark.loggr_test
class TestLogger(unittest.TestCase):
    #recuerda todos los metodos que inicien con test_ seran añadidos a la lista de pruebas.
    # los que inicien de manera diferente seran vistos como utilidades de clase y no contaran para las pruebas.

    def test_arch(self):
        # este test debera de ser utilizado para validar que haz completado todos los requisitios de diseño.
        obj = DTAF.logger
        for att in data["logger"]:
            self.assertTrue(hasattr(obj, att))
            #obj = getattr(obj,att)
            # verificamos que cada atributo tenga su documentacion.
        # self.assertTrue(getattr(obj, ".__doc__") not in ["", None])

    def test_add_log(self):
        log = logging.getLogger('master_log')
        result = add_log_reg("int1", weakref.ref(log))
        self.assertEqual(result, True)

    def test_create_logger(self):
        result = create_logger("EH1", "DEBUG")
        self.assertTrue(type(result) is logging.Logger)

    def test_del_logger(self):
        log = logging.getLogger("example")
        log.setLevel(logging.DEBUG)
        result = del_logger("example")
        self.assertTrue(type(result) is logging.Logger)

    def test_terminal_handler(self):
        log = logging.getLogger("example")
        log.setLevel(logging.DEBUG)
        result = config_terminal_handler('%(asctime)s - %(name)s - %(levelname) -8s - %(message)s')
        self.assertTrue(type(result) is logging.StreamHandler)

    def test_file_handler(self):
        log = logging.getLogger("example")
        log.setLevel(logging.DEBUG)
        result = config_file_handler(log, '%(asctime)s - %(name)s - %(levelname) -8s - %(message)s')
        #self.assertTrue(type(result) is logging.FileHandler)
        self.assertIsInstance(result, logging.FileHandler)

    def test_add_handler(self):
        log = logging.getLogger("example")
        log.setLevel(logging.DEBUG)
        result = add_handler(log, "Terminal", '%(asctime)s - %(name)s - %(levelname) -8s - %(message)s', mode="a")
        self.assertIsInstance(result, logging.StreamHandler)
        #self.assertEqual(result, True)

    def test_add_trace(self):
        add_trace_level()
        self.assertEqual(logging.getLevelName(9), "TRACE")
        self.assertIn("TRACE", logging._nameToLevel)
        self.assertIn(9, logging._levelToName)

    def test_assure_default_loggers(self):
        names: dict = {
            "SystemLogger": "DTAF_System",
            "DeviceLogger": "DTAF_Devices",
            "InterfaceLogger": "DTAF_Interfaces",
        }
        logger_instance: logging.Logger = None
        # checks that we have all default logger instances.
        for key in names:

            # asserts key is in DTAF.logger
            self.assertIn(key, dir(DTAF.logger))
            logger_instance = getattr(DTAF.logger, key)

            # Checks that the global is an instance of logging.Logger
            self.assertIsInstance(logger_instance, logging.Logger)

            # Ensures that we're using the correct configuration for each logger.
            config = Config.Logger.logger_config.get(names[key], None)
            target_level = config.get("level", None)

            # ensures that we have values
            self.assertTrue(config is not None)
            self.assertTrue(target_level is not None)

            # converst values to compare.
            if isinstance(target_level, str):
                target_level = target_level.upper()
                # assures that conifg matches valid names.
                self.assertIn(target_level, _nameToLevel)
                target_level = _nameToLevel[target_level]
            elif isinstance(target_level, int):
                self.assertIn(target_level, _levelToName)

            self.assertEqual(getattr(logger_instance, "level"), target_level)
            self.assertEqual(getattr(logger_instance, "name"), names[key])
            logger_instance.setLevel(0)
            for loglevel in _nameToLevel:
                if loglevel in ("NOTSET", "WARN"):
                    continue
                emit = getattr(logger_instance, loglevel.lower())
                emit(f"{key}: {logger_instance.name} TEST LOGGING EMIT FOR LEVEL `{loglevel}`")
            logger_instance.trace(f"{key} ::: {logger_instance.name} TEST LOGGING EMIT FOR LEVEL `TRACE`")

        pass

    # añadir prueba de monkeypatch para sys.stdout, esto para
    # que la informacion impresa sea realmente lo que esperamos
    # en el formato indicado.
    # logica:
    # inicias las variables
    # indicas informacion de prueba (lo que quieres imprimir, tal como lo haria un cliente)
    # Indicas informacion de validacion (lo que esperas que el modulo muestre al cliente)
    # generas un frame de parche (see pytest patch) para capturar la infomacion de sys.stdout (salida de sistema)
    #    Con el frame parchado
    #    Captura la informacion saliente al parche
    #    Valida que la informacion saliente coincida con lo que esperabas se mandara en el formato indicado

    # realiza un parche por cada formatter aplicado.


# add_trace_level()
# log=create_logger("log1","INFO")
# add_handler(log,"File", '%(levelname)s - %(name)s - %(asctime) -8s - %(message)s')
# log.debug("DEBUG")
# log.info("info")
# log.trace("trace")
# log2=create_logger("log2","DEBUG")
# add_handler(log,"Terminal", '%(levelname)s - %(name)s - %(asctime) -8s - %(message)s')
# print(global_logger_list)
