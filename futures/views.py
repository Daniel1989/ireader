import json

from django.forms import model_to_dict
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from futures.models import Goods, Market, GoodsItem


# Create your views here.
@csrf_exempt
def goods(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print(data)
        Goods.objects.create(**data)
        return JsonResponse({"success": True}, safe=False)
    return JsonResponse({"success": False}, safe=False)

@csrf_exempt
def market(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        Market.objects.create(**data)
        return JsonResponse({"success": True}, safe=False)
    return JsonResponse({"success": False}, safe=False)

@csrf_exempt
def edit(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        market = Market.objects.filter(date=data.get('date')).first()
        goods = Goods.objects.filter(date=data.get('date'), name=data.get('name')).first()
        if market is not None:
            market.market = data.get('market')
            market.save()
        if goods is not None:
            for key, value in data.items():
                if key != 'market':
                    setattr(goods, key, value)
                goods.save()
        return JsonResponse({"success": True}, safe=False)
    return JsonResponse({"success": False}, safe=False)

def list(request):
    date = request.GET.get('date')
    goods = request.GET.get('goods')
    if goods is None:
        data = Goods.objects.filter(date=date).order_by('created')
        market = Market.objects.filter(date=date).first()
        return JsonResponse([{
            **model_to_dict(item),
            "market": market.market if market else ''
        } for item in data], safe=False)
    else:
        data = Goods.objects.filter(name=goods).order_by('-date')
        market = Market.objects.all().order_by('-date')
        if len(data) != len(market):
            return JsonResponse([{
                **model_to_dict(item),
            } for item in data], safe=False)
        else:
            return JsonResponse([{
                **model_to_dict(data[index]),
                "market": market[index].market
            } for index, item in enumerate(data)], safe=False)


def goodslist(request):
    data = GoodsItem.objects.all().order_by('created')
    return JsonResponse([item.name for item in data], safe=False)