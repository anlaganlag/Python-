    def SaveAtMQ(self, jsonData, ch, method):
        #首先是jsonData就是数据的主题部分
        #ch就是channel..
        #method就是运输的时的标签和属性

        #同步链接
        connection = pika.BlockingConnection(self.Parameters)  # 创建连接
        #保持激活
        connection.process_data_events()  # 在执行长时间任务时，定时调用 process_data_events 方法，就不会丢失连接
        #建立管道
        channel = connection.channel()  # 建立管道
        print(jsonData)
        #宣告队列,队列的名称
        channel.queue_declare(queue='AmazonFollowSaleCrawler', durable=True)  # 是否队列持久化
        #通道的发布..
        channel.basic_publish(exchange='',  # 交换机
                              routing_key='AmazonFollowSaleCrawler',  # 路由键，写明将消息发往哪个队列
                              body=f'{jsonData}',
                              properties=pika.BasicProperties(
                                  delivery_mode=2, )  # delivery_mode=2 消息持久化
                              )  # 生产者要发送的消息
        ch.basic_ack(delivery_tag=method.delivery_tag)  # MQ确认消费
        connection.close()
