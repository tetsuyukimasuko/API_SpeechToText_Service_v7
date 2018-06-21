from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import ConferenceList,ConferenceLog,Organization,User
from .serializers import ConferenceInfoSerializer, ConferenceLogSerializer,OrganizationSerializer,UserSerializer
from .permissions import IsStaffOrTargetUser, IsAdmin, IsStaffOrTargetOrg,IsStaffOrTargetDict,IsStaffOrTargetConf
from rest_framework.permissions import AllowAny
import requests
from .WatsonSpeechRecognition import WatsonSTT
import json
from django.http import HttpResponse, Http404

#認証用API
class LoginViewSet(viewsets.ModelViewSet):
    queryset=User.objects.all()
    serializer_class=UserSerializer

    #認証済みユーザーじゃないとアクセスできない
    permission_classes=(IsAuthenticated,)

    #GETのみ許可
    def list(self, request, *args, **kwargs):
        return Response({"status" : "successfully authenticated."}, status=status.HTTP_200_OK)
    
    #残りは全て禁止
    def retrieve(self, request, *args, **kwargs):
        return Response({"detail": "メソッド  'GET' は許されていません。"},status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
        return Response({"detail": "メソッド  'DELETE' は許されていません。"},status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        return Response({"detail": "メソッド  'PUT' は許されていません。"},status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def create(self, request, *args, **kwargs):
        return Response({"detail": "メソッド  'POST' は許されていません。"},status=status.HTTP_405_METHOD_NOT_ALLOWED)
        
#ユーザーの本登録
#今は無効になっている
class UserRegisterViewSet(viewsets.ModelViewSet):
    queryset=User.objects.all()
    serializer_class=UserSerializer

    def list(self, request, user_id):
        try:
            u=User.objects.get(pk=user_id)
        except:
            return Http404()

        if u.is_active:
            return HttpResponse('既に認証済みです。')
        else:
            u.is_active=True
            u.save()
            return HttpResponse('本登録が完了しました。')

#ユーザー情報を参照・変更・追加する
class UserViewSet(viewsets.ModelViewSet):
    queryset=User.objects.all()
    serializer_class=UserSerializer

    #全ユーザーの情報を参照できるのはstaffのみ。
    #インスタンスを見られるのはstaffとその人自身だけ。
    def get_permissions(self):
        # allow non-authenticated user to create via POST
        return (AllowAny() if self.request.method == 'POST'
                else IsStaffOrTargetUser()),

#組織情報
class OrganizationViewSet(viewsets.ModelViewSet):
    queryset=Organization.objects.all()
    serializer_class=OrganizationSerializer

    #組織情報はシークレット。staffのみ操作可能。
    permission_classes=(IsAdmin,)

#組織の構成員を参照する。登録や更新には使用しない。
#構成員の一覧が欲しい場合に使う。
class OrganizationMemberViewSet(viewsets.ModelViewSet):
    queryset=User.objects.all()
    serializer_class=UserSerializer

    #staffか、その組織の構成員じゃないと見られない
    def get_permissions(self):
        return (IsStaffOrTargetDict,)

    def list(self, request, org_id):
        org=Organization.objects.get(org_id=org_id)
        member=User.objects.filter(org=org).order_by('username')
        return Response(member.values('id','username', 'email'),status=status.HTTP_200_OK)

    #残りは全て禁止
    def retrieve(self, request, *args, **kwargs):
        return Response({"detail": "メソッド  'GET' は許されていません。"},status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
        return Response({"detail": "メソッド  'DELETE' は許されていません。"},status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        return Response({"detail": "メソッド  'PUT' は許されていません。"},status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def create(self, request, *args, **kwargs):
        return Response({"detail": "メソッド  'POST' は許されていません。"},status=status.HTTP_405_METHOD_NOT_ALLOWED)




#単語登録を行う。POSTとGET(インスタンス)のみ許可。
#当該組織に所属している人のみアクセス・更新できる。
class CustomModelViewSet(viewsets.ModelViewSet):
    queryset=Organization.objects.all()
    serializer_class=OrganizationSerializer

    #全辞書の情報を参照できるのはstaffのみ。
    #特定の会社の辞書を閲覧・更新できるのはその会社の人とstaffだけ。
    def get_permissions(self):
        # allow non-authenticated user to create via POST
        return (IsStaffOrTargetDict()),

    #POSTをオーバーライド。org_IDと登録したい単語を載せてリクエストする。
    #これ結構時間かかるので、javascrip側のバックグラウンドでやりたいですね
    def create(self, request, org_id):

        try:
            org=Organization.objects.get(pk=org_id)
        except:
            return Response({'detail' : '見つかりませんでした。'},status=status.HTTP_404_NOT_FOUND)

        custom_words=request.POST['words']
        custom_words=json.loads(custom_words)

        #watsonの認証情報を引っ張ってくる
        org=Organization.objects.get(pk=org_id)
        watson_user_id=org.watson_user_id
        watson_user_pass=org.watson_user_pass

        WSTT=WatsonSTT(watson_user_id,watson_user_pass)

        #ここで、カスタムモデルを作成する。
        #既に存在する場合はそのidが返ってくる。
        custom_model_id=WSTT.CreateCustomModel(org.org_name+'の辞書',model='ja')

        word_registered=WSTT.AddCustomWords(custom_model_id,custom_words)

        return Response(word_registered,status=status.HTTP_201_CREATED)

    #GETをオーバーライド。登録単語を参照できる。
    def list(self, request, org_id):

        try:
            org=Organization.objects.get(pk=org_id)
        except:
            return Response({'detail' : '見つかりませんでした。'},status=status.HTTP_404_NOT_FOUND)

        #watsonの認証情報を引っ張ってくる
        org=Organization.objects.get(pk=org_id)
        watson_user_id=org.watson_user_id
        watson_user_pass=org.watson_user_pass

        WSTT=WatsonSTT(watson_user_id,watson_user_pass)

        #ここで、カスタムモデルを作成する。
        #既に存在する場合はそのidが返ってくる。
        custom_model_id=WSTT.CreateCustomModel(org.org_name+'の辞書',model='ja')
        word_registered=WSTT.GetCustomWords(custom_model_id)

        return Response(word_registered,status=status.HTTP_200_OK)

    #他は禁止。カスタムモデルの削除、単語の更新、削除は全てPOSTで一括でやる
    def retrieve(self, request, *args, **kwargs):
        return Response({"detail": "メソッド  'GET' は許されていません。"},status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
        return Response({"detail": "メソッド  'DELETE' は許されていません。"},status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        return Response({"detail": "メソッド  'PUT' は許されていません。"},status=status.HTTP_405_METHOD_NOT_ALLOWED)



#会議情報を参照する。
#会議新規作成→エンドポイント : /api/conference/, メソッド : POST。speaker_listにはユーザーIDのリストを入れてポストする。
#会議情報参照→エンドポイント : /api/conference/<conf_ID>/, メソッド : GET。
class ConferenceViewSet(viewsets.ModelViewSet):
    queryset=ConferenceList.objects.all()
    serializer_class=ConferenceInfoSerializer

    #全会議情報を参照できるのはstaffのみ。
    #特定の会社の会議情報を閲覧・更新できるのはその会社の人とstaffだけ。
    def get_permissions(self):
        return (IsStaffOrTargetOrg()),

    #自分が呼ばれている会議のみリストアップ。スタッフなら全部見られる。
    def list(self, request, *args, **kwargs):
        if request.user.is_staff:
            return super().list(self, request, *args, **kwargs)
        else:
            conferences=request.user.conferences.values()
            return Response(conferences,status=status.HTTP_200_OK)
    



#会議ログを参照、または追加、更新する。
#会議ログ追加→エンドポイント : /api/conference/<conf_ID>/log/, メソッド : POST
#会議ログ全参照→エンドポイント : /api/conference/<conf_ID>/log/, メソッド : GET
#発言単体の参照と更新→エンドポイント : /api/conference/<conf_ID>/log/<index>/, メソッド : GET,PUT
class ConferenceLogViewSet(viewsets.ModelViewSet):
    queryset=ConferenceLog.objects.all()
    serializer_class=ConferenceLogSerializer


    #全会議ログを参照できるのはstaffのみ。
    #特定の会議のログを閲覧・更新できるのはその会議の参加者とstaffだけ。
    def get_permissions(self):
        # allow non-authenticated user to create via POST
        return (IsStaffOrTargetConf()),

    #POSTをオーバーライド。ポスト時は、ファイルを渡すとテキスト化してくれる。
    def create(self, request, conf_id):

        #格納先の会議情報を取得
        try:
            clist=ConferenceList.objects.get(pk=conf_id)
        except:
            return Response({'detail' : '会議IDが正しくありません。'},status=status.HTTP_404_NOT_FOUND)

        #データを取得
        try:
            timestamp=request.POST['timestamp']
            speaker_name=request.POST['speaker_name']
            language=request.POST['language']
            file=request.FILES['wav']
            use_custom_model=request.POST['use_custom_model']
        except:
            return Response({'detail' : 'POSTするjsonの形式が違います。'},status=status.HTTP_400_BAD_REQUEST)        
        
        #watsonの認証情報を引っ張ってくる
        org=clist.org_id
        watson_user_id=org.watson_user_id
        watson_user_pass=org.watson_user_pass

        #テキスト化
        WSTT=WatsonSTT(watson_user_id,watson_user_pass)
        
        if use_custom_model:
            custom_model_id=WSTT.GetCustomModelByName(org.org_name+'の辞書')
            text=WSTT.RecognizeAudio(file,customization_id=custom_model_id,delete_interjection=True,model=language)
        else:
            text=WSTT.RecognizeAudio(file,delete_interjection=True,model=language)

        #データを保存
        if text=='unrecognized':
            return Response({'speaker' : speaker_name, 'timestamp' : timestamp, 'result' : text, 'note' : '認識できなかったためデータを破棄しました。'},status=status.HTTP_200_OK)
        else:
            c=ConferenceLog(conf_id=clist, timestamp=timestamp, text=text, speaker_name=speaker_name)
            c.save()

        return Response({'speaker' : speaker_name, 'timestamp' : timestamp, 'result' : text},status=status.HTTP_201_CREATED)

    #GETをオーバーライド。timestampでソート。
    def list(self, request, conf_id):
        log=ConferenceLog.objects.filter(conf_id=conf_id)
        log=log.order_by('timestamp')
        if len(log)>0:
            return Response(log.values(),status=status.HTTP_200_OK)
        else:
            return Response({'detail' : '会議IDが正しくないか、ログがまだありません。'},status=status.HTTP_404_NOT_FOUND)

    #インスタンスのGETをオーバーライド。IDではなく、インデックスでアクセスできるようにする。
    def retrieve(self, request, conf_id, pk):
        
        #ソートされたログを出力
        try:
            log=ConferenceLog.objects.filter(conf_id=conf_id)
        except:
            return Response({'detail' : '会議IDが正しくないか、ログがまだありません。'},status=status.HTTP_404_NOT_FOUND)

        log=log.order_by('timestamp')
        log=log.values()

        #会議ログがある場合
        if len(log)>0:

            #pk番目を取り出す。pkは0から始まる。
            #例外処理
            try:
                num=int(pk)
            except:
                return Response({'detail' : 'インデックスには整数を指定してください。'},status=status.HTTP_400_BAD_REQUEST)
            if num>len(log)-1:
                return Response({'detail' : 'インデックスが範囲外です。'},status=status.HTTP_404_NOT_FOUND)
            else:
                single_log=log[num]
                return Response(single_log,status=status.HTTP_200_OK) 
        
        #会議ログがない場合
        else:
            return Response({'detail' : 'インデックスが範囲外です。'},status=status.HTTP_404_NOT_FOUND)


    #TODO PUTをオーバーライド。pkではなくindexでアクセス。
    #PUT時はtextのみ編集可能。
    def update(self, request, conf_id, pk):

        #ソートされたログを出力
        try:
            log=ConferenceLog.objects.filter(conf_id=conf_id)
        except:
            return Response({'detail' : '会議IDが正しくないか、ログがまだありません。'},status=status.HTTP_404_NOT_FOUND)

        log=log.order_by('timestamp')
        log=log.values()

        #会議ログがある場合
        if len(log)>0:

            #pk番目を取り出す。pkは0から始まる。
            #例外処理
            try:
                num=int(pk)
            except:
                return Response({'detail' : 'インデックスには整数を指定してください。'},status=status.HTTP_400_BAD_REQUEST)
            if num>len(log)-1:
                return Response({'detail' : 'インデックスが範囲外です。'},status=status.HTTP_404_NOT_FOUND)
            else:
                single_log=log[num]
                spoken_id=single_log['spoken_id']
                target=ConferenceLog.objects.get(pk=spoken_id)
                target.text=request.POST['text']
                target.save()
                return Response(target,status=status.HTTP_201_CREATED)
        
        #会議ログがない場合
        else:
            return Response({'detail' : 'インデックスが範囲外です。'},status=status.HTTP_404_NOT_FOUND)

        return super().update(request, *args, **kwargs)

    #DELETEは禁止
    def destroy(self, request, *args, **kwargs):
        return Response({"detail": "メソッド  'DELETE' は許されていません。"},status=status.HTTP_405_METHOD_NOT_ALLOWED)
