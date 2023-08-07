import utils
import fonts


def lambda_handler(event, context):
    query_string_parameters = event.get('queryStringParameters', {})

    if not query_string_parameters:
        return {
            "statusCode": 400,
            "body": "handle parameter is required"
        }

    handle = query_string_parameters.get('handle', None)

    if not handle:
        return {
            "statusCode": 400,
            "body": "handle parameter is required"
        }

    user = utils.get_user_data(handle)

    if not user:
        return {
            "statusCode": 404,
            "body": f"{handle} not found"
        }

    tier_text = utils.arena_tier_to_text(user.arena_tier)
    tier_info = utils.get_tier_info(tier_text)

    max_tier_text = utils.arena_tier_to_text(user.arena_max_tier)
    percentage = (user.arena_rating - tier_info.min_rating) / \
        (tier_info.max_rating - tier_info.min_rating) * 300 + 25

    svg = '''\
<?xml version="1.0" encoding="UTF-8"?>
<svg
    width="350"
    height="170"
    viewBox="0 0 350 170"
    fill="none"
    version="1.1"
    xmlns="http://www.w3.org/2000/svg"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xml:space="preserve"
>
    <style type="text/css">
        @font-face {{
            font-family: 'Inter';
            font-weight: regular;
            src: url(data:font/ttf;charset=utf-8;base64,{inter_font_regular});
        }}
        @font-face {{
            font-family: 'Inter';
            font-weight: bold;
            src: url(data:font/ttf;charset=utf-8;base64,{inter_font_bold});
        }}
        @keyframes delayFadeIn {{
            0%{{
                opacity:0
            }}
            60%{{
                opacity:0
            }}
            100%{{
                opacity:1
            }}
        }}
        @keyframes fadeIn {{
            from {{
                opacity: 0;
            }}
            to {{
                opacity: 1;
            }}
        }}
        @keyframes rateBarAnimation {{
            0% {{
                stroke-dashoffset: {percentage};
            }}
            75% {{
                stroke-dashoffset: 25;
            }}
            100% {{
                stroke-dashoffset: 25;
            }}
        }}

        .username {{
            font-family: 'Inter', sans-serif;
            font-size: 24px;
            font-weight: bold;
            animation: fadeIn 0.8s ease-in-out forwards;
        }}
        .tier {{
            font-family: 'Inter', sans-serif;
            font-size: 40px;
            font-weight: bold;
            fill : rgba(255, 255, 255, 0.75);
            animation: fadeIn 0.8s ease-in-out forwards;
        }}
        .info {{
            font-family: 'Inter', sans-serif;
            font-size: 14px;
            animation: delayFadeIn 1s ease-in-out forwards;
        }}
        .info-value {{
            font-family: 'Inter', sans-serif;
            font-size: 12px;
            animation: delayFadeIn 1s ease-in-out forwards;
        }}
        .detail {{
            font-family: 'Inter', sans-serif;
            font-size: 10px;
            animation: delayFadeIn 1s ease-in-out forwards;
        }}
        .rate-bar {{
            stroke-dasharray: {percentage};
            stroke-dashoffset: {percentage};
            animation: rateBarAnimation 3s forwards ease-in-out;
            animation-delay: 1s;
            border-radius: 3px;
            stroke: #FFFFFF;
            stroke-width: 4;
        }}
        .rate-bar-container {{
            animation: delayFadeIn 1s ease-in-out forwards;
            stroke: #FFFFFF;
            stroke-opacity: 0.5;
            stroke-width: 4;
        }}
    </style>
    <rect width="350" height="170" fill="{color}" rx = "6"/>
    <g>
        <text x="25" y="44" fill="#ffffff" class = "username">
            {username}
        </text>
        <text x="325" y="55"  fill="#F6F6DB" text-anchor="end" class = "tier">
            {tier}
        </text>
    </g>
    <g>
        <text x="25" y="76" fill="#ffffff" class = "info">
            Rating
        </text>
        <text x="125" y="76" fill="#ffffff" class = "info-value">
            {tier} {rating} (max: {max_rating})
        </text>
    </g>
    <g>
        <text x="25" y="93" fill="#ffffff" class = "info">
            Performance
        </text>
        <text x="125" y="93" fill="#ffffff" class = "info-value">
            {performance}
        </text>
    </g>
    <g>
        <text x="25" y="110" fill="#ffffff" class = "info">
            Matches
        </text>
        <text x="125" y="110" fill="#ffffff" class = "info-value">
            {matches}
        </text>
    </g>
    <g>
        <line x1="25" y1="133" x2="325" y2="133" class="rate-bar-container"/>
    </g>
    <g>
        <line x1="25" y1="133" x2="{percentage}" y2="133" class="rate-bar"/>
    </g>
    <g>
        <text x="325" y="147" text-anchor="end" fill="#ffffff" class = "detail">
            {rating} / {next_rating}
        </text>
    </g>
</svg>
    '''.format(
        username=user.username,
        tier=f"{tier_text}",
        rating=f"{user.arena_rating}",
        max_rating=f"{max_tier_text} {user.arena_max_rating}",
        next_rating=tier_info.max_rating,
        performance=user.arena_recent_performance,
        matches=user.arena_match_count,
        color=tier_info.color,
        percentage=percentage,
        inter_font_regular=fonts.regular,
        inter_font_bold=fonts.bold
    )

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'image/svg+xml',
            'Cache-Control': 'max-age=1800'
        },
        'body': svg,
    }
