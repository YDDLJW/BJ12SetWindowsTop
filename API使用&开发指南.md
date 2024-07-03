# API开发/使用指南

- 网络协议：http
- 地址：127.0.0.1:8212
- URL：`/SetWindowsTopAPI`
- 完整使用示例：`/SetWindowsTopAPI/current_windows` //获取所有当前打开的窗口信息列表

### 目录
1. [获取所有当前打开的窗口信息列表](#获取所有当前打开的窗口信息列表)
2. [获取曾经打开过的所有窗口信息列表](#获取曾经打开过的所有窗口信息列表)
3. [获取特定当前窗口信息](#获取特定当前窗口信息)
4. [修改特定窗口的笔记](#修改特定窗口的笔记)
5. [置顶或取消置顶特定窗口](#置顶或取消置顶特定窗口)

### 获取所有当前打开的窗口信息列表

- URL: `/current_windows`
- 方法：GET
- 查询参数
  - 无
- 响应参数

    | 参数名称       | 参数含义    | 参数类型    | 是否必填 | 备注             |
    |------------|---------|---------|------|----------------|
    | id         | id      | Integer | 是    |                |
    | name       | 窗口名称    | String  | 是    |                |
    | hwnd       | 窗口句柄    | String  | 是    |                |
    | is_set_top | 窗口是否被置顶 | Integer | 是    | 0为False，1为True |
    | notes      | 窗口笔记    | String  | 否    |                |
  - 示例
    ```json
    [
      {
          "id": 1,  //id
          "name": "Window1",  //窗口名称
          "hwnd": "123456", //窗口句柄
          "is_set_top": 0, //窗口是否被置顶
          "notes": "Main application window"  //窗口笔记
      },
      {
          "id": 2,
          "name": "Window2",
          "hwnd": "654321",
          "is_set_top": 0,
          "notes": "Secondary application window"
      }
    ]
    ```

### 获取曾经打开过的所有窗口信息列表

- URL: `/all_windows`
- 方法：GET
- 查询参数
  - 无
- 响应参数

    | 参数名称  | 参数含义 | 参数类型    | 是否必填 | 备注     |
    |-------|------|---------|------|--------|
    | id    | id   | Integer | 是    |        |
    | name  | 窗口名称 | String  | 是    |        |
    | date  | 日期   | String  | 是    | 上次更新时间 |
    | notes | 窗口笔记 | String  | 否    |        |
  - 示例
    ```json
    [
        {
            "id": 1,  //id
            "name": "window1",  //窗口名称
            "date": "2024-07-03 13:04", //日期
            "notes": "Main application window" //窗口笔记
        },
        {
            "id": 2,
            "name": "window2",
            "date": "2024-07-03 13:04",
            "notes": "Secondary application window"
        },
        {
            "id": 3,
            "name": "window3",
            "date": "2024-07-03 13:04",
            "notes": "Third application window not in current windows"
        }
    ]
    ```

### 获取特定当前窗口信息

- URL: `/current_windows/detail?name=<name\>&hwnd=<hwnd\>`
- 方法：GET
- 查询参数

    | 参数名称 | 参数含义 | 参数类型   | 是否必填 | 备注 |
    |------|------|--------|------|----|
    | name | 窗口名称 | String | 否    |    |
    | hwnd | 窗口句柄 | String | 是    |    |
  - 示例
      ```json
      {
          "name": "Window1",  //窗口名称
          "hwnd": "123456" //窗口句柄
      }
      ```
- 响应参数

    | 参数名称       | 参数含义    | 参数类型    | 是否必填 | 备注             |
    |------------|---------|---------|------|----------------|
    | id         | id      | Integer | 是    |                |
    | name       | 窗口名称    | String  | 是    |                |
    | hwnd       | 窗口句柄    | String  | 是    |                |
    | is_set_top | 窗口是否被置顶 | Integer | 是    | 0为False，1为True |
    | notes      | 窗口笔记    | String  | 否    |                |
  - 示例
    ```json
    {
        "id": 1,  //id
        "name": "Window1",  //窗口名称
        "hwnd": "123456", //窗口句柄
        "is_set_top": 0, //窗口是否被置顶
        "notes": "Main application window"  //窗口笔记
    }
    ```

### 修改特定窗口的笔记

- URL: `/all_windows/detail?name=<name\>&notes=<notes\>`
- 方法：POST
- 注意：不要使用 `/current_windows/detail`
- 查询参数

    | 参数名称  | 参数含义 | 参数类型    | 是否必填 | 备注 |
    |-------|------|---------|------|----|
    | id    | id   | Integer | 是    |    |
    | name  | 窗口名称 | String  | 是    |    |
    | notes | 窗口笔记 | String  | 否    |    |
  - 示例
    ```json
    {
        "id": "1",  //id
        "name": "Window1",  //窗口名称
        "notes": "Main application window note update" //窗口笔记
    }
    ```
- 响应参数

    | 参数名称  | 参数含义 | 参数类型    | 是否必填 | 备注     |
    |-------|------|---------|------|--------|
    | id    | id   | Integer | 是    |        |
    | name  | 窗口名称 | String  | 是    |        |
    | date  | 日期   | String  | 是    | 上次更新时间 |
    | notes | 窗口笔记 | String  | 否    |        |
  - 示例
    ```json
    {
        "id": 1,  //id
        "name": "Window1",  //窗口名称
        "date": "2024-07-03 13:04", //日期
        "notes": "Main application window note update"  //窗口笔记
    }
    ```

### 置顶或取消置顶特定窗口

- URL: `/current_windows/toggle_set_top?name=<name\>&hwnd=<hwnd\>`
- 方法：POST
- 注意：不需要传输`is_set_top`参数
- 查询参数

    | 参数名称       | 参数含义    | 参数类型    | 是否必填 | 备注    |
    |------------|---------|---------|------|-------|
    | name       | 窗口名称    | String  | 否    |       |
    | hwnd       | 窗口句柄    | String  | 是    |       |
  - 示例
    ```json
    {
        "name": "Window1",  //窗口名称
        "hwnd": "123456", //窗口句柄
    }
    ```
- 响应参数

    | 参数名称       | 参数含义    | 参数类型    | 是否必填 | 备注                                                    |
    |------------|---------|---------|------|-------------------------------------------------------|
    | id         | id      | Integer | 是    |                                                       |
    | name       | 窗口名称    | String  | 是    |                                                       |
    | hwnd       | 窗口句柄    | String  | 是    |                                                       |
    | is_set_top | 窗口是否被置顶 | Integer | 是    | 0为False，1为True。<br/>当值原本为0时，会更新为1；<br/>当值原本为1时，会更新为0。 |
    | notes      | 窗口笔记    | String  | 否    |                                                       |
  - 示例
    ```json
    {
        "id": 2,  //id
        "name": "window2", //窗口名称
        "hwnd": "1234", //窗口句柄
        "is_set_top": 1,  //窗口是否被置顶
        "notes": "this is window 2" //窗口笔记
    }
    ```
