#!/usr/bin/env python3

'''
Created on 24.12.2017

@author: dz

Listen to all traffic on MQTT/UDP, pump updates to MQTT broker
'''

# will work even if package is not installed
import sys
sys.path.append('..')
#sys.path.append('../mqttudp')

import threading
#import re

import mqttudp.engine as me
import mqttudp.interlock
import mqttudp.config as cfg

import paho.mqtt.client as broker

SUBSCRIBE_TOPIC="#"
MQTT_BROKER_HOST="192.168.86.23"
MQTT_BROKER_PORT=1883

ilock = mqttudp.interlock.Bidirectional(5)

class mqttudp_bridge:

  def __init__(self, logger):
    self.logger = logger

  def broker_on_connect(self, client, userdata, rc, unkn):  # @UnusedVariable
      #print("Connected with result code "+str(rc))
      self.logger.info("Connected with result code "+str(rc))
      client.subscribe(SUBSCRIBE_TOPIC)

  def broker_on_message(self, client, userdata, msg):  # @UnusedVariable
      #print( msg )
  #    if (len(blackList) > 0) and (re.match( blackList, msg.topic )):
      if cfg.check_black_list(msg.topic, blackList):
          self.logger.info("To UDP BLACKLIST: "+ msg.topic+" "+str(msg.payload))
          #print("To UDP BLACKLIST: "+ msg.topic+" "+str(msg.payload))
          return
      if ilock.broker_to_udp(msg.topic, msg.payload):
          # TODO msg.payload = gatewayv3.convertmsg(msg.payload)
          me.send_publish( msg.topic, msg.payload )
          self.logger.info("To UDP: "+msg.topic+"="+str(msg.payload))
          #print("To UDP: "+msg.topic+"="+str(msg.payload))
      else:
          #print("BLOCKED to UDP: "+msg.topic+"="+str(msg.payload))
          self.logger.info("BLOCKED to UDP: "+msg.topic+"="+str(msg.payload))

  def broker_listen_thread(self, bclient):
      bclient.loop_forever()


  def recv_packet_from_udp(self, pkt):
      global last
      if pkt.ptype != me.PacketType.Publish:
          return
      if last.__contains__(pkt.topic) and last[pkt.topic] == pkt.value:
          return
      last[pkt.topic] = pkt.value
      if ilock.udp_to_broker(pkt.topic, pkt.value):
          bclient.publish(pkt.topic, pkt.value, qos=0)
          #print( "From UDP: "+topic+"="+value )
          self.logger.info( "From UDP: "+pkt.topic+"="+pkt.value )
      else:
          #print( "BLOCKED from UDP: "+topic+"="+value )
          self.logger.info( "BLOCKED from UDP: "+pkt.topic+"="+pkt.value )

  def udp_listen_thread(self, bclient):
      global last
      last = {}
      me.listen(self.recv_packet_from_udp)


  def start_bridge(self):
    print( "Will exchange all the traffic between MQTT/UDP and MQTT broker at "+MQTT_BROKER_HOST )

    bclient = broker.Client()
    bclient.on_connect = self.broker_on_connect
    bclient.on_message = self.broker_on_message

    bclient.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)
    #print("connected", bclient)
    self.logger.info( "connected " + str(bclient) )

    blt = threading.Thread(target=self.broker_listen_thread, args=(bclient,))
    ult = threading.Thread(target=self.udp_listen_thread, args=(bclient,))

    blt.start()
    ult.start()

    blt.join()
    ult.join()