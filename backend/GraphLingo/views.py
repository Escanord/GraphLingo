import json
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from inference.question_inference import main
from argparse import Namespace

def index(request):
    return HttpResponse("Hello")

class DialogView(APIView):
    def post(self, request, format=None):
        data = request.data
        print(data)
        args = Namespace()
        args.question = data['msg']
        if 'save_session' in data['data']:
            args.save_session = data['data']['save_session'] 
        else:
            args.save_session = False
        
        if 'followup' in data['data']:
            args.followup = data['data']['followup']
        else:
             args.followup = False
        if 'explorativeRate' in data['data']:
            args.explorative_rate = data['data']['explorativeRate']
        else:
            args.explorative_rate = 0.001    
        name2kg = {
            'gpt' : 'neo4j',
            'crux': 'cruxkg',
            'prime': 'drugkg'
        }
        args.kg = 'neo4j'
        if 'database' in data['data'] and data['data']['database'] in name2kg:
            args.kg = name2kg[data['data']['database']]
        response, suggestions, nodes, edges = main(args)
        body = {
            'msg': response,
            'data': {
                'suggestions': suggestions,
                'graph': {
                    'nodes': nodes,
                    'edges': edges
                }
            }
        }
        return Response(body, status=status.HTTP_200_OK)