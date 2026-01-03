Compiled from "SourceFile"
public abstract class a.a {
  public static java.lang.String a(java.lang.String);
    Code:
       0: new           #11                 // class java/lang/StringBuilder
       3: dup
       4: astore_1
       5: invokespecial #15                 // Method java/lang/StringBuilder."<init>":()V
       8: new           #17                 // class java/io/BufferedReader
      11: dup
      12: astore_2
      13: new           #19                 // class java/io/FileReader
      16: dup
      17: astore_3
      18: aload_0
      19: invokespecial #22                 // Method java/io/FileReader."<init>":(Ljava/lang/String;)V
      22: aload_3
      23: invokespecial #25                 // Method java/io/BufferedReader."<init>":(Ljava/io/Reader;)V
      26: aload_2
      27: invokevirtual #29                 // Method java/io/BufferedReader.readLine:()Ljava/lang/String;
      30: dup
      31: astore_0
      32: ifnull        44
      35: aload_1
      36: aload_0
      37: invokevirtual #33                 // Method java/lang/StringBuilder.append:(Ljava/lang/String;)Ljava/lang/StringBuilder;
      40: pop
      41: goto          26
      44: aload_2
      45: invokevirtual #36                 // Method java/io/BufferedReader.close:()V
      48: goto          69
      51: astore_0
      52: aload_2
      53: invokevirtual #36                 // Method java/io/BufferedReader.close:()V
      56: goto          64
      59: aload_0
      60: swap
      61: invokevirtual #42                 // Method java/lang/Throwable.addSuppressed:(Ljava/lang/Throwable;)V
      64: aload_0
      65: athrow
      66: invokevirtual #47                 // Method java/lang/Throwable.printStackTrace:()V
      69: aload_1
      70: invokevirtual #50                 // Method java/lang/StringBuilder.toString:()Ljava/lang/String;
      73: areturn
    Exception table:
       from    to  target type
           8    11    66   Class java/io/IOException
          13    16    66   Class java/io/IOException
          18    26    66   Class java/io/IOException
          26    30    51   any
          35    40    51   any
          44    51    66   Class java/io/IOException
          52    59    59   any
          59    66    66   Class java/io/IOException
    LineNumberTable:
      line 1: 0
      line 2: 8
      line 4: 27
      line 6: 37
      line 8: 45
      line 9: 53
      line 16: 66
      line 18: 70
}
