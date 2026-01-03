Compiled from "SourceFile"
public class ai.guiji.duix.sdk.client.loader.ModelInfo$Region implements java.io.Serializable {
  public static final int TYPE_SILENCE;

  public static final int TYPE_MOTION;

  public java.lang.String name;

  public int type;

  public java.util.List<ai.guiji.duix.sdk.client.loader.ModelInfo$Frame> frames;

  public ai.guiji.duix.sdk.client.loader.ModelInfo$Region(int, java.lang.String);
    Code:
       0: aload_0
       1: dup
       2: dup
       3: dup2
       4: invokespecial #31                 // Method java/lang/Object."<init>":()V
       7: ldc           #33                 // String
       9: putfield      #35                 // Field name:Ljava/lang/String;
      12: new           #37                 // class java/util/ArrayList
      15: dup
      16: astore_0
      17: invokespecial #38                 // Method java/util/ArrayList."<init>":()V
      20: aload_0
      21: putfield      #40                 // Field frames:Ljava/util/List;
      24: iload_1
      25: putfield      #42                 // Field type:I
      28: aload_2
      29: putfield      #35                 // Field name:Ljava/lang/String;
      32: return
    LineNumberTable:
      line 1: 4
      line 2: 7
      line 4: 12
      line 7: 25
      line 8: 29

  public java.lang.String toString();
    Code:
       0: new           #46                 // class java/lang/StringBuilder
       3: dup
       4: aload_0
       5: swap
       6: ldc           #48                 // String Region{type=
       8: invokespecial #51                 // Method java/lang/StringBuilder."<init>":(Ljava/lang/String;)V
      11: getfield      #42                 // Field type:I
      14: invokevirtual #55                 // Method java/lang/StringBuilder.append:(I)Ljava/lang/StringBuilder;
      17: ldc           #57                 // String , name=
      19: invokevirtual #60                 // Method java/lang/StringBuilder.append:(Ljava/lang/String;)Ljava/lang/StringBuilder;
      22: aload_0
      23: getfield      #35                 // Field name:Ljava/lang/String;
      26: invokevirtual #60                 // Method java/lang/StringBuilder.append:(Ljava/lang/String;)Ljava/lang/StringBuilder;
      29: ldc           #62                 // String , frames=
      31: invokevirtual #60                 // Method java/lang/StringBuilder.append:(Ljava/lang/String;)Ljava/lang/StringBuilder;
      34: aload_0
      35: getfield      #40                 // Field frames:Ljava/util/List;
      38: invokeinterface #68,  1           // InterfaceMethod java/util/List.size:()I
      43: invokevirtual #55                 // Method java/lang/StringBuilder.append:(I)Ljava/lang/StringBuilder;
      46: bipush        125
      48: invokevirtual #71                 // Method java/lang/StringBuilder.append:(C)Ljava/lang/StringBuilder;
      51: invokevirtual #73                 // Method java/lang/StringBuilder.toString:()Ljava/lang/String;
      54: areturn
    LineNumberTable:
      line 1: 0
      line 4: 38
}
