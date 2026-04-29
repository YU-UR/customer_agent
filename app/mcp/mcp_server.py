import random

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(name="ResourceDemo", log_level="INFO", host="0.0.0.0", port=8000)


@mcp.tool()
def get_order_status():
    """[order]这是一个获取订单状态的工具"""
    order_status = random.choice(["已发货", "未发货", "运送中"])
    return order_status


@mcp.tool()
def get_order_list(order_status=None):
    """[order]这是获取用户未完成订单列表"""

    order_list = [
        {
            "orderId": "SO202410150001",
            "status": "已发货",
            "details": {
                "customerName": "张伟",
                "productName": "无线蓝牙耳机",
                "quantity": 1,
                "unitPrice": 299.00,
                "totalAmount": 299.00,
                "orderTime": "2024-10-15 10:30:00",
                "shippingAddress": "北京市朝阳区建国门外大街1号",
                "paymentMethod": "支付宝",
                "trackingNumber": "SF1234567890"
            }
        },
        {
            "orderId": "SO202410150002",
            "status": "待付款",
            "details": {
                "customerName": "李娜",
                "productName": "智能手机 128GB",
                "quantity": 1,
                "unitPrice": 2599.00,
                "totalAmount": 2599.00,
                "orderTime": "2024-10-15 14:20:00",
                "shippingAddress": "上海市浦东新区陆家嘴环路1000号",
                "paymentMethod": "待支付",
                "expiryTime": "2024-10-16 14:20:00"
            }
        },
        {
            "orderId": "SO202410150003",
            "status": "已完成",
            "details": {
                "customerName": "王磊",
                "productName": "运动跑步鞋 42码",
                "quantity": 1,
                "unitPrice": 458.00,
                "totalAmount": 458.00,
                "orderTime": "2024-10-14 09:15:00",
                "shippingAddress": "广州市天河区体育西路123号",
                "paymentMethod": "微信支付",
                "completionTime": "2024-10-15 16:45:00"
            }
        }
    ]
    return order_list


@mcp.tool()
def get_product_type():
    """[product] 这是获取产品类型的工具"""

    product_type = [
        "电脑", "手机", "键盘", "鼠标", "显示器"
    ]

    return product_type


@mcp.tool()
def get_product_brand():
    """[product] 这是获取产品品牌的工具"""
    product_brand = [
        "苹果", "华为", "AOC", "cherry", "雷蛇", "华硕"
    ]
    return product_brand


@mcp.tool()
def get_product_detail():
    """[product] 这是获取产品详情工具"""
    products = [
        {
            "productId": "P202410150001",
            "productName": "Apple iPhone 15 Pro 128GB 原色钛金属",
            "category": "智能手机",
            "brand": "Apple",
            "price": 7999.00,
            "specifications": {
                "屏幕": "6.1英寸超视网膜XDR显示屏",
                "芯片": "A17 Pro芯片",
                "存储": "128GB",
                "摄像头": "4800万像素三摄系统"
            },
            "stock": 150
        },
        {
            "productId": "P202410150002",
            "productName": "Huawei MateBook X Pro 2024 13.9英寸",
            "category": "笔记本电脑",
            "brand": "华为",
            "price": 8999.00,
            "specifications": {
                "屏幕": "13.9英寸3K触控全面屏",
                "处理器": "Intel Core i7-1360P",
                "内存": "16GB LPDDR5",
                "存储": "1TB SSD"
            },
            "stock": 80
        },
        {
            "productId": "P202410150003",
            "productName": "Cherry MX3.0S 机械键盘 红轴",
            "category": "键盘",
            "brand": "Cherry",
            "price": 699.00,
            "specifications": {
                "轴体": "Cherry MX红轴",
                "连接方式": "有线",
                "布局": "108键全尺寸",
                "背光": "红色背光"
            },
            "stock": 200
        },
        {
            "productId": "P202410150004",
            "productName": "Razer DeathAdder V3 游戏鼠标",
            "category": "鼠标",
            "brand": "雷蛇",
            "price": 599.00,
            "specifications": {
                "传感器": "Focus Pro 30K光学传感器",
                "DPI": "30000",
                "连接": "有线/2.4GHz无线",
                "重量": "58g"
            },
            "stock": 150
        },
        {
            "productId": "P202410150005",
            "productName": "AOC 27G2SP 27英寸电竞显示器",
            "category": "显示器",
            "brand": "AOC",
            "price": 1299.00,
            "specifications": {
                "尺寸": "27英寸",
                "分辨率": "1920x1080",
                "刷新率": "165Hz",
                "面板": "IPS"
            },
            "stock": 100
        },
        {
            "productId": "P202410150006",
            "productName": "ASUS ROG Strix SCAR 16 游戏本",
            "category": "笔记本电脑",
            "brand": "华硕",
            "price": 15999.00,
            "specifications": {
                "屏幕": "16英寸2.5K 240Hz",
                "处理器": "Intel i9-14900HX",
                "显卡": "RTX 4070 8GB",
                "内存": "32GB DDR5"
            },
            "stock": 50
        },
        {
            "productId": "P202410150007",
            "productName": "Huawei Mate 60 Pro 512GB",
            "category": "智能手机",
            "brand": "华为",
            "price": 6999.00,
            "specifications": {
                "屏幕": "6.82英寸OLED",
                "芯片": "麒麟9000S",
                "存储": "512GB",
                "摄像头": "5000万像素三摄"
            },
            "stock": 120
        },
        {
            "productId": "P202410150008",
            "productName": "Apple MacBook Air 13 M2芯片",
            "category": "笔记本电脑",
            "brand": "Apple",
            "price": 8999.00,
            "specifications": {
                "屏幕": "13.6英寸Liquid视网膜",
                "芯片": "Apple M2",
                "内存": "8GB",
                "存储": "256GB SSD"
            },
            "stock": 90
        },
        {
            "productId": "P202410150009",
            "productName": "Razer BlackWidow V4 机械键盘",
            "category": "键盘",
            "brand": "雷蛇",
            "price": 1299.00,
            "specifications": {
                "轴体": "Razer绿轴",
                "连接": "有线",
                "布局": "104键",
                "背光": "RGB幻彩"
            },
            "stock": 80
        },
        {
            "productId": "P202410150010",
            "productName": "ASUS ROG Swift PG32UCDM 显示器",
            "category": "显示器",
            "brand": "华硕",
            "price": 8999.00,
            "specifications": {
                "尺寸": "32英寸",
                "分辨率": "3840x2160",
                "刷新率": "240Hz",
                "面板": "OLED"
            },
            "stock": 30
        },
        {
            "productId": "P202410150011",
            "productName": "Apple iPhone 14 128GB 星光色",
            "category": "智能手机",
            "brand": "Apple",
            "price": 5999.00,
            "specifications": {
                "屏幕": "6.1英寸超视网膜XDR显示屏",
                "芯片": "A15仿生芯片",
                "存储": "128GB",
                "摄像头": "1200万像素双摄系统"
            },
            "stock": 180
        },
        {
            "productId": "P202410150012",
            "productName": "HuaMateBook 14s 2024 14.2英寸",
            "category": "笔记本电脑",
            "brand": "华为",
            "price": 6999.00,
            "specifications": {
                "屏幕": "14.2英寸2.5K触控屏",
                "处理器": "Intel Core i5-13500H",
                "内存": "16GB LPDDR5",
                "存储": "512GB SSD"
            },
            "stock": 95
        },
        {
            "productId": "P202410150013",
            "productName": "Cherry MX8.2 TKL 机械键盘 茶轴",
            "category": "键盘",
            "brand": "Cherry",
            "price": 1299.00,
            "specifications": {
                "轴体": "Cherry MX茶轴",
                "连接方式": "有线+蓝牙+2.4G三模",
                "布局": "87键紧凑布局",
                "背光": "RGB炫彩背光"
            },
            "stock": 75
        },
        {
            "productId": "P202410150014",
            "productName": "Razer Viper V2 Pro 无线游戏鼠标",
            "category": "鼠标",
            "brand": "雷蛇",
            "price": 899.00,
            "specifications": {
                "传感器": "Focus Pro 30K光学传感器",
                "DPI": "30000",
                "连接": "2.4GHz无线",
                "重量": "58g"
            },
            "stock": 120
        },
        {
            "productId": "P202410150015",
            "productName": "AOC Q27G3XMN 27英寸电竞显示器",
            "category": "显示器",
            "brand": "AOC",
            "price": 1999.00,
            "specifications": {
                "尺寸": "27英寸",
                "分辨率": "2560x1440",
                "刷新率": "180Hz",
                "面板": "VA"
            },
            "stock": 85
        },
        {
            "productId": "P202410150016",
            "productName": "ASUS TUF Gaming F15 游戏本",
            "category": "笔记本电脑",
            "brand": "华硕",
            "price": 7999.00,
            "specifications": {
                "屏幕": "15.6英寸FHD 144Hz",
                "处理器": "Intel i7-13650HX",
                "显卡": "RTX 4060 8GB",
                "内存": "16GB DDR5"
            },
            "stock": 60
        },
        {
            "productId": "P202410150017",
            "productName": "Huawei nova 12 256GB",
            "category": "智能手机",
            "brand": "华为",
            "price": 2999.00,
            "specifications": {
                "屏幕": "6.7英寸OLED",
                "芯片": "骁龙778G",
                "存储": "256GB",
                "摄像头": "5000万像素主摄"
            },
            "stock": 200
        },
        {
            "productId": "P202410150018",
            "productName": "Apple MacBook Pro 16 M3 Pro芯片",
            "category": "笔记本电脑",
            "brand": "Apple",
            "price": 19999.00,
            "specifications": {
                "屏幕": "16.2英寸Liquid视网膜XDR",
                "芯片": "Apple M3 Pro",
                "内存": "18GB",
                "存储": "512GB SSD"
            },
            "stock": 40
        },
        {
            "productId": "P202410150019",
            "productName": "Razer Huntsman V2 光学键盘",
            "category": "键盘",
            "brand": "雷蛇",
            "price": 1499.00,
            "specifications": {
                "轴体": "雷蛇光学红轴",
                "连接": "有线",
                "布局": "104键全尺寸",
                "背光": "RGB幻彩"
            },
            "stock": 65
        },
        {
            "productId": "P202410150020",
            "productName": "ASUS ProArt PA279CRV 显示器",
            "category": "显示器",
            "brand": "华硕",
            "price": 4599.00,
            "specifications": {
                "尺寸": "27英寸",
                "分辨率": "3840x2160",
                "刷新率": "120Hz",
                "面板": "IPS"
            },
            "stock": 45
        },
        {
            "productId": "P202410150021",
            "productName": "Apple iPad Air 11英寸 M2芯片",
            "category": "平板电脑",
            "brand": "Apple",
            "price": 4799.00,
            "specifications": {
                "屏幕": "11英寸Liquid视网膜",
                "芯片": "M2芯片",
                "存储": "128GB",
                "网络": "Wi-Fi"
            },
            "stock": 110
        },
        {
            "productId": "P202410150022",
            "productName": "Huawei WATCH GT 4 46mm",
            "category": "智能手表",
            "brand": "华为",
            "price": 1488.00,
            "specifications": {
                "屏幕": "1.43英寸AMOLED",
                "续航": "14天超长续航",
                "功能": "100+运动模式",
                "材质": "不锈钢表体"
            },
            "stock": 150
        },
        {
            "productId": "P202410150023",
            "productName": "Cherry G80-3000S TKL 机械键盘",
            "category": "键盘",
            "brand": "Cherry",
            "price": 499.00,
            "specifications": {
                "轴体": "Cherry MX青轴",
                "连接方式": "有线",
                "布局": "87键",
                "背光": "无光"
            },
            "stock": 180
        },
        {
            "productId": "P202410150024",
            "productName": "Razer Basilisk V3 有线鼠标",
            "category": "鼠标",
            "brand": "雷蛇",
            "price": 499.00,
            "specifications": {
                "传感器": "Focus+ 26K光学传感器",
                "DPI": "26000",
                "连接": "有线",
                "重量": "101g"
            },
            "stock": 135
        },
        {
            "productId": "P202410150025",
            "productName": "AOC 24B2XH 23.8英寸显示器",
            "category": "显示器",
            "brand": "AOC",
            "price": 699.00,
            "specifications": {
                "尺寸": "23.8英寸",
                "分辨率": "1920x1080",
                "刷新率": "75Hz",
                "面板": "IPS"
            },
            "stock": 200
        },
        {
            "productId": "P202410150026",
            "productName": "ASUS Zenbook 14 OLED 2024",
            "category": "笔记本电脑",
            "brand": "华硕",
            "price": 6999.00,
            "specifications": {
                "屏幕": "14英寸2.8K OLED",
                "处理器": "Intel Core i5-13420H",
                "内存": "16GB LPDDR5",
                "存储": "512GB SSD"
            },
            "stock": 70
        },
        {
            "productId": "P202410150027",
            "productName": "Apple AirPods Pro (第二代)",
            "category": "耳机",
            "brand": "Apple",
            "price": 1899.00,
            "specifications": {
                "降噪": "主动降噪",
                "续航": "6小时(降噪开)",
                "充电": "MagSafe充电盒",
                "功能": "自适应通透模式"
            },
            "stock": 250
        },
        {
            "productId": "P202410150028",
            "productName": "Huawei FreeBuds Pro 3",
            "category": "耳机",
            "brand": "华为",
            "price": 1499.00,
            "specifications": {
                "降噪": "智能动态降噪",
                "续航": "6.5小时(降噪开)",
                "充电": "无线充电",
                "功能": "高清空间音频"
            },
            "stock": 180
        },
        {
            "productId": "P202410150029",
            "productName": "Razer BlackShark V2 Pro 耳机",
            "category": "耳机",
            "brand": "雷蛇",
            "price": 1099.00,
            "specifications": {
                "类型": "无线游戏耳机",
                "续航": "24小时",
                "连接": "2.4GHz",
                "麦克风": "可拆卸心形指向麦克风"
            },
            "stock": 90
        },
        {
            "productId": "P202410150030",
            "productName": "ASUS ROG Delta S 游戏耳机",
            "category": "耳机",
            "brand": "华硕",
            "price": 1299.00,
            "specifications": {
                "类型": "有线游戏耳机",
                "驱动单元": "50mm ASUS Essence",
                "接口": "USB-C",
                "特色": "AI降噪麦克风"
            },
            "stock": 80
        }
    ]
    return products


if __name__ == '__main__':
    mcp.run(transport="sse")
