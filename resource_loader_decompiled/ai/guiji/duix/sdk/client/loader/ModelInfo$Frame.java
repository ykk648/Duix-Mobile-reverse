Compiled from "SourceFile"
public class ai.guiji.duix.sdk.client.loader.ModelInfo$Frame implements java.io.Serializable {
  public int index;

  public java.lang.String rawPath;

  public java.lang.String maskPath;

  public java.lang.String sgPath;

  public int[] rect;

  public boolean startFlag;

  public boolean endFlag;

  public java.lang.String actionName;

  public ai.guiji.duix.sdk.client.loader.ModelInfo$Frame();
    Code:
       0: aload_0
       1: invokespecial #28                 // Method java/lang/Object."<init>":()V
       4: return

  public boolean check();
    Code:
       0: aload_0
       1: getfield      #32                 // Field rawPath:Ljava/lang/String;
       4: invokestatic  #38                 // Method android/text/TextUtils.isEmpty:(Ljava/lang/CharSequence;)Z
       7: ifne          21
      10: aload_0
      11: getfield      #40                 // Field rect:[I
      14: ifnull        21
      17: iconst_1
      18: goto          22
      21: iconst_0
      22: ireturn
    LineNumberTable:
      line 1: 1

  public java.lang.String toString();
    Code:
       0: new           #44                 // class java/lang/StringBuilder
       3: dup
       4: aload_0
       5: swap
       6: ldc           #46                 // String Frame{index=
       8: invokespecial #49                 // Method java/lang/StringBuilder."<init>":(Ljava/lang/String;)V
      11: getfield      #51                 // Field index:I
      14: invokevirtual #55                 // Method java/lang/StringBuilder.append:(I)Ljava/lang/StringBuilder;
      17: ldc           #57                 // String , rawPath=\'
      19: invokevirtual #60                 // Method java/lang/StringBuilder.append:(Ljava/lang/String;)Ljava/lang/StringBuilder;
      22: aload_0
      23: getfield      #32                 // Field rawPath:Ljava/lang/String;
      26: invokevirtual #60                 // Method java/lang/StringBuilder.append:(Ljava/lang/String;)Ljava/lang/StringBuilder;
      29: ldc           #62                 // String \', maskPath=\'
      31: invokevirtual #60                 // Method java/lang/StringBuilder.append:(Ljava/lang/String;)Ljava/lang/StringBuilder;
      34: aload_0
      35: getfield      #64                 // Field maskPath:Ljava/lang/String;
      38: invokevirtual #60                 // Method java/lang/StringBuilder.append:(Ljava/lang/String;)Ljava/lang/StringBuilder;
      41: ldc           #66                 // String \', sgPath=\'
      43: invokevirtual #60                 // Method java/lang/StringBuilder.append:(Ljava/lang/String;)Ljava/lang/StringBuilder;
      46: aload_0
      47: getfield      #68                 // Field sgPath:Ljava/lang/String;
      50: invokevirtual #60                 // Method java/lang/StringBuilder.append:(Ljava/lang/String;)Ljava/lang/StringBuilder;
      53: ldc           #70                 // String \', rect=
      55: invokevirtual #60                 // Method java/lang/StringBuilder.append:(Ljava/lang/String;)Ljava/lang/StringBuilder;
      58: aload_0
      59: getfield      #40                 // Field rect:[I
      62: invokestatic  #75                 // Method java/util/Arrays.toString:([I)Ljava/lang/String;
      65: invokevirtual #60                 // Method java/lang/StringBuilder.append:(Ljava/lang/String;)Ljava/lang/StringBuilder;
      68: ldc           #77                 // String , startFlag=
      70: invokevirtual #60                 // Method java/lang/StringBuilder.append:(Ljava/lang/String;)Ljava/lang/StringBuilder;
      73: aload_0
      74: getfield      #79                 // Field startFlag:Z
      77: invokevirtual #82                 // Method java/lang/StringBuilder.append:(Z)Ljava/lang/StringBuilder;
      80: ldc           #84                 // String , endFlag=
      82: invokevirtual #60                 // Method java/lang/StringBuilder.append:(Ljava/lang/String;)Ljava/lang/StringBuilder;
      85: aload_0
      86: getfield      #86                 // Field endFlag:Z
      89: invokevirtual #82                 // Method java/lang/StringBuilder.append:(Z)Ljava/lang/StringBuilder;
      92: ldc           #88                 // String , actionName=\'
      94: invokevirtual #60                 // Method java/lang/StringBuilder.append:(Ljava/lang/String;)Ljava/lang/StringBuilder;
      97: aload_0
      98: getfield      #90                 // Field actionName:Ljava/lang/String;
     101: invokevirtual #60                 // Method java/lang/StringBuilder.append:(Ljava/lang/String;)Ljava/lang/StringBuilder;
     104: ldc           #92                 // String \'}
     106: invokevirtual #60                 // Method java/lang/StringBuilder.append:(Ljava/lang/String;)Ljava/lang/StringBuilder;
     109: invokevirtual #94                 // Method java/lang/StringBuilder.toString:()Ljava/lang/String;
     112: areturn
    LineNumberTable:
      line 1: 0
      line 6: 62
}
