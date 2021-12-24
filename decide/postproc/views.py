from rest_framework.views import APIView
from rest_framework.response import Response


class PostProcView(APIView):

    def identity(self, options):
        out = []

        for opt in options:
            out.append({
                **opt,
                'postproc': opt['votes'],
            });

        out.sort(key=lambda x: -x['postproc'])
        return out


    def proportional_representation(self, options, type): #EGC-GUADALENTIN
        out = []
        votes = []
        points_for_opt = []
        #Sainte Lague reparte los escaños de forma más equitativa, penalizando en mayor medida mientras más escaños tenga una opción
        multiplier = 2 if type == 'SAINTE_LAGUE' else 1
        points = options[0]['points']
        zero_votes = True

        for i in range(0, len(options)):
            votes.append(options[i]['votes'])
            points_for_opt.append(0)
            if zero_votes is True and options[i]['votes'] != 0:
                zero_votes = False

        if zero_votes is False:
            for i in range(0, points):
                max_index = votes.index(max(votes))
                points_for_opt[max_index] += 1
                votes[max_index] = options[max_index]['votes'] / (multiplier * points_for_opt[max_index] + 1)

        for i in range(0, len(options)):
            out.append({
                **options[i],
                'postproc': points_for_opt[i],
            })

        out.sort(key=lambda x: (-x['postproc'], -x['votes']))
        return out

    def post(self, request):

        """
         * type: IDENTITY | EQUALITY | WEIGHT
         * options: [
            {
             option: str,
             number: int,
             votes: int,
             ...extraparams
            }
           ]
        """

        out = []
        questions = request.data

        for q in questions:
            result = None
            t = q['type']
            opts = q['options']

            if t == 'IDENTITY':
                result = self.identity(opts)

            if t == 'HONDT' or t == 'SAINTE_LAGUE':
                result = self.proportional_representation(opts, t)

            out.append({'type': t, 'options': result})


        return Response(out)
