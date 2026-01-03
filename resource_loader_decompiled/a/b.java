Compiled from "SourceFile"
public final class a.b implements java.lang.Runnable {
  public final android.content.Context a;

  public a.b(android.content.Context);
    Code:
       0: aload_0
       1: dup
       2: invokespecial #16                 // Method java/lang/Object."<init>":()V
       5: aload_1
       6: putfield      #18                 // Field a:Landroid/content/Context;
       9: return
    LineNumberTable:
      line 1: 2
      line 2: 6

  public final void run();
    Code:
       0: aload_0
       1: ldc           #21                 // String
       3: astore_1
       4: ldc           #21                 // String
       6: astore_2
       7: aconst_null
       8: astore_3
       9: ldc           #23                 // String https://vshow.guiji.ai/duix-guiji-cn/sysEventReport/report
      11: astore        4
      13: new           #25                 // class java/net/URL
      16: dup
      17: aload         4
      19: invokespecial #28                 // Method java/net/URL."<init>":(Ljava/lang/String;)V
      22: invokevirtual #32                 // Method java/net/URL.openConnection:()Ljava/net/URLConnection;
      25: checkcast     #34                 // class java/net/HttpURLConnection
      28: dup
      29: dup2
      30: dup2
      31: dup2
      32: astore        4
      34: sipush        5000
      37: invokevirtual #40                 // Method java/net/URLConnection.setReadTimeout:(I)V
      40: sipush        5000
      43: invokevirtual #43                 // Method java/net/URLConnection.setConnectTimeout:(I)V
      46: ldc           #45                 // String POST
      48: invokevirtual #48                 // Method java/net/HttpURLConnection.setRequestMethod:(Ljava/lang/String;)V
      51: iconst_1
      52: invokevirtual #52                 // Method java/net/URLConnection.setDoOutput:(Z)V
      55: ldc           #54                 // String Connection
      57: ldc           #56                 // String Keep-Alive
      59: invokevirtual #60                 // Method java/net/URLConnection.setRequestProperty:(Ljava/lang/String;Ljava/lang/String;)V
      62: ldc           #62                 // String Content-Type
      64: ldc           #64                 // String application/json;charset=UTF-8
      66: invokevirtual #60                 // Method java/net/URLConnection.setRequestProperty:(Ljava/lang/String;Ljava/lang/String;)V
      69: invokevirtual #67                 // Method java/net/URLConnection.connect:()V
      72: new           #69                 // class org/json/JSONObject
      75: dup
      76: astore        5
      78: aload_0
      79: dup
      80: dup
      81: dup2
      82: aload         5
      84: invokespecial #70                 // Method org/json/JSONObject."<init>":()V
      87: getfield      #18                 // Field a:Landroid/content/Context;
      90: invokevirtual #76                 // Method android/content/Context.getApplicationContext:()Landroid/content/Context;
      93: invokevirtual #80                 // Method android/content/Context.getResources:()Landroid/content/res/Resources;
      96: invokevirtual #86                 // Method android/content/res/Resources.getDisplayMetrics:()Landroid/util/DisplayMetrics;
      99: dup
     100: getfield      #92                 // Field android/util/DisplayMetrics.widthPixels:I
     103: istore        6
     105: getfield      #95                 // Field android/util/DisplayMetrics.heightPixels:I
     108: istore        7
     110: getstatic     #100                // Field android/os/Build$VERSION.SDK_INT:I
     113: istore        8
     115: getstatic     #106                // Field android/os/Build.MANUFACTURER:Ljava/lang/String;
     118: astore        9
     120: getstatic     #109                // Field android/os/Build.MODEL:Ljava/lang/String;
     123: astore        10
     125: getfield      #18                 // Field a:Landroid/content/Context;
     128: invokevirtual #76                 // Method android/content/Context.getApplicationContext:()Landroid/content/Context;
     131: invokevirtual #113                // Method android/content/Context.getApplicationInfo:()Landroid/content/pm/ApplicationInfo;
     134: astore        11
     136: getfield      #18                 // Field a:Landroid/content/Context;
     139: invokevirtual #76                 // Method android/content/Context.getApplicationContext:()Landroid/content/Context;
     142: invokevirtual #117                // Method android/content/Context.getPackageManager:()Landroid/content/pm/PackageManager;
     145: aload         11
     147: invokevirtual #123                // Method android/content/pm/PackageManager.getApplicationLabel:(Landroid/content/pm/ApplicationInfo;)Ljava/lang/CharSequence;
     150: invokeinterface #129,  1          // InterfaceMethod java/lang/CharSequence.toString:()Ljava/lang/String;
     155: astore        11
     157: getfield      #18                 // Field a:Landroid/content/Context;
     160: invokevirtual #76                 // Method android/content/Context.getApplicationContext:()Landroid/content/Context;
     163: invokevirtual #117                // Method android/content/Context.getPackageManager:()Landroid/content/pm/PackageManager;
     166: aload_0
     167: getfield      #18                 // Field a:Landroid/content/Context;
     170: invokevirtual #132                // Method android/content/Context.getPackageName:()Ljava/lang/String;
     173: iconst_0
     174: invokevirtual #136                // Method android/content/pm/PackageManager.getPackageInfo:(Ljava/lang/String;I)Landroid/content/pm/PackageInfo;
     177: getfield      #141                // Field android/content/pm/PackageInfo.versionName:Ljava/lang/String;
     180: astore_0
     181: getfield      #18                 // Field a:Landroid/content/Context;
     184: invokevirtual #132                // Method android/content/Context.getPackageName:()Ljava/lang/String;
     187: astore        12
     189: ldc           #143                // String eventType
     191: ldc           #145                // String OPEN_SDK_CLIENT_PROPERTIES
     193: invokevirtual #149                // Method org/json/JSONObject.put:(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;
     196: pop
     197: new           #69                 // class org/json/JSONObject
     200: dup
     201: dup2
     202: dup2
     203: dup2
     204: dup2
     205: astore        13
     207: invokespecial #70                 // Method org/json/JSONObject."<init>":()V
     210: ldc           #151                // String screenWidth
     212: iload         6
     214: invokevirtual #154                // Method org/json/JSONObject.put:(Ljava/lang/String;I)Lorg/json/JSONObject;
     217: pop
     218: ldc           #156                // String screenHeight
     220: iload         7
     222: invokevirtual #154                // Method org/json/JSONObject.put:(Ljava/lang/String;I)Lorg/json/JSONObject;
     225: pop
     226: ldc           #158                // String deviceName
     228: new           #160                // class java/lang/StringBuilder
     231: dup
     232: aload         9
     234: swap
     235: invokespecial #161                // Method java/lang/StringBuilder."<init>":()V
     238: invokevirtual #165                // Method java/lang/StringBuilder.append:(Ljava/lang/String;)Ljava/lang/StringBuilder;
     241: ldc           #167                // String
     243: invokevirtual #165                // Method java/lang/StringBuilder.append:(Ljava/lang/String;)Ljava/lang/StringBuilder;
     246: aload         10
     248: invokevirtual #165                // Method java/lang/StringBuilder.append:(Ljava/lang/String;)Ljava/lang/StringBuilder;
     251: invokevirtual #168                // Method java/lang/StringBuilder.toString:()Ljava/lang/String;
     254: invokevirtual #149                // Method org/json/JSONObject.put:(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;
     257: pop
     258: ldc           #170                // String systemName
     260: ldc           #172                // String Android
     262: invokevirtual #149                // Method org/json/JSONObject.put:(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;
     265: pop
     266: ldc           #174                // String systemVersion
     268: new           #160                // class java/lang/StringBuilder
     271: dup
     272: iload         8
     274: swap
     275: aload_2
     276: invokespecial #175                // Method java/lang/StringBuilder."<init>":(Ljava/lang/String;)V
     279: invokevirtual #178                // Method java/lang/StringBuilder.append:(I)Ljava/lang/StringBuilder;
     282: invokevirtual #168                // Method java/lang/StringBuilder.toString:()Ljava/lang/String;
     285: invokevirtual #149                // Method org/json/JSONObject.put:(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;
     288: pop
     289: ldc           #180                // String appName
     291: aload         11
     293: invokevirtual #149                // Method org/json/JSONObject.put:(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;
     296: pop
     297: ldc           #182                // String packageName
     299: aload         12
     301: invokevirtual #149                // Method org/json/JSONObject.put:(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;
     304: pop
     305: ldc           #184                // String appVersion
     307: aload_0
     308: invokevirtual #149                // Method org/json/JSONObject.put:(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;
     311: pop
     312: ldc           #21                 // String
     314: astore_0
     315: getfield      #18                 // Field a:Landroid/content/Context;
     318: invokevirtual #188                // Method android/content/Context.getContentResolver:()Landroid/content/ContentResolver;
     321: ldc           #190                // String android_id
     323: invokestatic  #196                // Method android/provider/Settings$System.getString:(Landroid/content/ContentResolver;Ljava/lang/String;)Ljava/lang/String;
     326: astore_0
     327: goto          331
     330: pop
     331: aload         13
     333: dup
     334: ldc           #204                // String uuid
     336: aload_0
     337: invokevirtual #149                // Method org/json/JSONObject.put:(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;
     340: pop
     341: ldc           #206                // String ai.guiji.duix.sdk.client.Constant
     343: invokestatic  #212                // Method java/lang/Class.forName:(Ljava/lang/String;)Ljava/lang/Class;
     346: ldc           #214                // String VERSION_NAME
     348: invokevirtual #218                // Method java/lang/Class.getDeclaredField:(Ljava/lang/String;)Ljava/lang/reflect/Field;
     351: aconst_null
     352: invokevirtual #224                // Method java/lang/reflect/Field.get:(Ljava/lang/Object;)Ljava/lang/Object;
     355: astore_0
     356: ldc           #226                // String sdkVersion
     358: new           #160                // class java/lang/StringBuilder
     361: dup
     362: aload_0
     363: swap
     364: aload_1
     365: invokespecial #175                // Method java/lang/StringBuilder."<init>":(Ljava/lang/String;)V
     368: invokevirtual #229                // Method java/lang/StringBuilder.append:(Ljava/lang/Object;)Ljava/lang/StringBuilder;
     371: invokevirtual #168                // Method java/lang/StringBuilder.toString:()Ljava/lang/String;
     374: invokevirtual #149                // Method org/json/JSONObject.put:(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;
     377: pop
     378: goto          382
     381: pop
     382: aload         4
     384: dup
     385: aload         5
     387: dup
     388: ldc           #231                // String eventProperties
     390: aload         13
     392: invokevirtual #149                // Method org/json/JSONObject.put:(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;
     395: pop
     396: invokevirtual #232                // Method org/json/JSONObject.toString:()Ljava/lang/String;
     399: astore_0
     400: invokevirtual #236                // Method java/net/URLConnection.getOutputStream:()Ljava/io/OutputStream;
     403: dup
     404: dup
     405: aload_0
     406: invokevirtual #240                // Method java/lang/String.getBytes:()[B
     409: invokevirtual #246                // Method java/io/OutputStream.write:([B)V
     412: invokevirtual #249                // Method java/io/OutputStream.flush:()V
     415: invokevirtual #252                // Method java/io/OutputStream.close:()V
     418: invokevirtual #256                // Method java/net/HttpURLConnection.getResponseCode:()I
     421: sipush        200
     424: if_icmpne     477
     427: aload         4
     429: invokevirtual #260                // Method java/net/URLConnection.getInputStream:()Ljava/io/InputStream;
     432: astore_3
     433: new           #262                // class java/io/BufferedReader
     436: dup
     437: astore_0
     438: new           #264                // class java/io/InputStreamReader
     441: dup
     442: astore_1
     443: aload_3
     444: invokespecial #267                // Method java/io/InputStreamReader."<init>":(Ljava/io/InputStream;)V
     447: aload_1
     448: invokespecial #270                // Method java/io/BufferedReader."<init>":(Ljava/io/Reader;)V
     451: new           #160                // class java/lang/StringBuilder
     454: dup
     455: astore_1
     456: invokespecial #161                // Method java/lang/StringBuilder."<init>":()V
     459: aload_0
     460: invokevirtual #273                // Method java/io/BufferedReader.readLine:()Ljava/lang/String;
     463: dup
     464: astore_2
     465: ifnull        483
     468: aload_1
     469: aload_2
     470: invokevirtual #165                // Method java/lang/StringBuilder.append:(Ljava/lang/String;)Ljava/lang/StringBuilder;
     473: pop
     474: goto          459
     477: aload         4
     479: invokevirtual #276                // Method java/net/HttpURLConnection.getResponseMessage:()Ljava/lang/String;
     482: pop
     483: aload_3
     484: ifnull        518
     487: aload_3
     488: invokevirtual #277                // Method java/io/InputStream.close:()V
     491: goto          518
     494: astore_0
     495: goto          519
     498: astore_0
     499: aload_3
     500: aload_0
     501: invokevirtual #280                // Method java/lang/Object.toString:()Ljava/lang/String;
     504: pop
     505: ifnull        518
     508: aload_3
     509: invokevirtual #277                // Method java/io/InputStream.close:()V
     512: goto          518
     515: invokevirtual #285                // Method java/lang/Throwable.printStackTrace:()V
     518: return
     519: aload_3
     520: ifnull        533
     523: aload_3
     524: invokevirtual #277                // Method java/io/InputStream.close:()V
     527: goto          533
     530: invokevirtual #285                // Method java/lang/Throwable.printStackTrace:()V
     533: aload_0
     534: athrow
    Exception table:
       from    to  target type
           9    11   498   Class java/lang/Exception
           9    11   494   any
          13    28   498   Class java/lang/Exception
          13    28   494   any
          34    75   498   Class java/lang/Exception
          34    75   494   any
          78   103   498   Class java/lang/Exception
          78   103   494   any
         105   108   498   Class java/lang/Exception
         105   108   494   any
         110   113   498   Class java/lang/Exception
         110   113   494   any
         115   118   498   Class java/lang/Exception
         115   118   494   any
         120   123   498   Class java/lang/Exception
         120   123   494   any
         125   134   498   Class java/lang/Exception
         125   134   494   any
         136   155   498   Class java/lang/Exception
         136   155   494   any
         157   180   498   Class java/lang/Exception
         157   180   494   any
         181   187   498   Class java/lang/Exception
         181   187   494   any
         189   196   498   Class java/lang/Exception
         189   196   494   any
         197   200   498   Class java/lang/Exception
         197   200   494   any
         207   217   498   Class java/lang/Exception
         207   217   494   any
         218   225   498   Class java/lang/Exception
         218   225   494   any
         226   231   498   Class java/lang/Exception
         226   231   494   any
         232   257   498   Class java/lang/Exception
         232   257   494   any
         258   265   498   Class java/lang/Exception
         258   265   494   any
         266   271   498   Class java/lang/Exception
         266   271   494   any
         272   288   498   Class java/lang/Exception
         272   288   494   any
         289   296   498   Class java/lang/Exception
         289   296   494   any
         297   304   498   Class java/lang/Exception
         297   304   494   any
         305   311   498   Class java/lang/Exception
         305   311   494   any
         312   314   498   Class java/lang/Exception
         312   314   494   any
         315   326   330   Class java/lang/Exception
         315   326   494   any
         331   340   498   Class java/lang/Exception
         331   340   494   any
         341   355   381   Class java/lang/Exception
         341   355   494   any
         356   361   381   Class java/lang/Exception
         356   361   494   any
         362   377   381   Class java/lang/Exception
         362   377   494   any
         382   395   498   Class java/lang/Exception
         382   395   494   any
         396   399   498   Class java/lang/Exception
         396   399   494   any
         400   421   498   Class java/lang/Exception
         400   421   494   any
         427   432   498   Class java/lang/Exception
         427   432   494   any
         433   436   498   Class java/lang/Exception
         433   436   494   any
         438   441   498   Class java/lang/Exception
         438   441   494   any
         443   454   498   Class java/lang/Exception
         443   454   494   any
         456   463   498   Class java/lang/Exception
         456   463   494   any
         468   473   498   Class java/lang/Exception
         468   473   494   any
         477   482   498   Class java/lang/Exception
         477   482   494   any
         487   494   515   Class java/io/IOException
         499   504   494   any
         508   515   515   Class java/io/IOException
         523   530   530   Class java/io/IOException
    LineNumberTable:
      line 1: 9
      line 3: 13
      line 4: 22
      line 6: 37
      line 8: 43
      line 10: 46
      line 14: 52
      line 16: 55
      line 17: 62
      line 18: 69
      line 21: 72
      line 22: 87
      line 23: 100
      line 24: 105
      line 25: 110
      line 26: 115
      line 27: 120
      line 28: 125
      line 29: 136
      line 30: 157
      line 31: 181
      line 32: 189
      line 33: 197
      line 34: 210
      line 35: 218
      line 36: 226
      line 37: 258
      line 38: 266
      line 39: 289
      line 40: 297
      line 41: 305
      line 43: 312
      line 45: 315
      line 47: 334
      line 49: 341
      line 50: 346
      line 51: 352
      line 52: 356
      line 55: 388
      line 57: 396
      line 59: 400
      line 60: 406
      line 61: 412
      line 62: 415
      line 64: 418
      line 66: 429
      line 67: 433
      line 68: 451
      line 70: 460
      line 71: 470
      line 77: 479
      line 85: 488
      line 86: 501
      line 90: 509
      line 92: 515
      line 93: 524
      line 95: 530
      line 98: 534
}
