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

#消费要尝试5次..
    @retry(pika.exceptions.AMQPConnectionError, delay=5, jitter=(1, 3))  # MQ重连机制
    def taskScheduling(self):
        #首先是建立连接
        connection = pika.BlockingConnection(self.Parameters)  # 创建连接
        #保持通道存活
        connection.process_data_events()
        channel = connection.channel()  # 建立管道
        channel.queue_declare(queue='AmazonFollowSaleUrls', durable=True)  # 队列持久化
        channel.basic_qos(prefetch_count=100)  # 单个进程在MQ每次取得的消息量
        #消费需要用回调函数去处理
        channel.basic_consume('AmazonFollowSaleUrls',
                              self.callback)  # 消费消息  如果收到消息就 调用回调函数      ,auto_ack=True  读取消息之后数据删除
        print(' [*] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()  # 只要一运行  就一直在等待
